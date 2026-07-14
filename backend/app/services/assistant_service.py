"""Servicio del asistente "Ask AI" — consulta de datos por lenguaje natural.

Arquitectura: tool-use (function calling). Se le dan al modelo unas pocas
herramientas que son wrappers sobre los servicios que ya existen. El modelo
decide qué herramienta llamar; el backend la ejecuta **con el usuario actual**,
por lo que los permisos por módulo (ADR 0003) se aplican igual que en la UI. El
asistente es de **solo lectura**: nunca modifica datos.

Multi-proveedor: el LLM que responde puede ser Anthropic (Claude), DeepSeek,
Gemini o Groq, elegido con la variable de entorno ASSISTANT_PROVIDER. Este servicio solo habla
con la interfaz común `LLMProvider` (ver `llm_providers.py`); no conoce el
formato nativo de cada API — así el loop de tool-use, las tools, los permisos,
el presupuesto y la auditoría son un único código compartido entre proveedores.

Controles:
- Tope de gasto mensual (ASSISTANT_MONTHLY_BUDGET_USD): se contabiliza el costo
  real de cada llamada al modelo a partir de `usage`; al superar el tope el
  asistente se desactiva y pide contactar al administrador.
- Prompt caching (ASSISTANT_PROMPT_CACHE): cachea el prefijo estable (system +
  tools) para abaratar cada pregunta. Aplica al proveedor Anthropic; DeepSeek
  cachea automáticamente en su propio backend sin necesidad de este flag.
"""

import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.admission import Admission, AdmissionStatus
from app.models.assistant import AssistantUsage
from app.models.audit import AuditLog, OperationType
from app.models.user import Module, User
from app.services.llm_providers import ToolCall, build_provider

# Servicios existentes que reutilizamos como fuente de datos.
from app.services.finance_service import FinanceService
from app.services.occupancy_service import OccupancyService
from app.services.resident_service import ResidentService

logger = logging.getLogger(__name__)

_MAX_TOOL_ITERATIONS = 5


def _provider_api_errors() -> tuple:
    """Clases de excepción de error de API de los SDKs instalados.

    Import perezoso: cada SDK solo se importa si ya está instalado (puede
    faltar alguno si solo se usa un subconjunto de proveedores).
    """
    errors = []
    try:
        import anthropic

        errors.append(anthropic.APIError)
    except ImportError:
        pass
    try:
        import openai

        errors.append(openai.APIError)
    except ImportError:
        pass
    try:
        from google.genai import errors as genai_errors

        errors.append(genai_errors.APIError)
    except ImportError:
        pass
    return tuple(errors) or (Exception,)


_PROVIDER_API_ERRORS = _provider_api_errors()


_PROVIDER_LABELS = {"deepseek": "DeepSeek", "gemini": "Gemini", "groq": "Groq"}


def _provider_label() -> str:
    return _PROVIDER_LABELS.get(settings.ASSISTANT_PROVIDER, "Anthropic")


def _model_label() -> str:
    """Nombre human-readable del modelo activo para mostrar en la UI."""
    provider = settings.ASSISTANT_PROVIDER
    if provider == "gemini":
        model = settings.ASSISTANT_MODEL_GEMINI
        if "2.5" in model:
            return "Gemini 2.5 Flash"
        if "2.0" in model:
            return "Gemini 2.0 Flash"
        return "Gemini Flash"
    elif provider == "deepseek":
        model = settings.ASSISTANT_MODEL_DEEPSEEK
        if "reasoner" in model:
            return "DeepSeek Reasoner"
        return "DeepSeek Chat"
    elif provider == "groq":
        model = settings.ASSISTANT_MODEL_GROQ
        if "8b" in model:
            return "Groq Llama 3.1 8B"
        return "Groq Llama 3.3 70B"
    else:  # anthropic
        model = settings.ASSISTANT_MODEL_ANTHROPIC
        if "opus" in model:
            return "Claude Opus 4.8"
        elif "sonnet" in model:
            return "Claude Sonnet 5"
        return "Claude Haiku 4.5"

# Estados de admisión que cuentan como "activa" (residente internado ahora).
# Misma definición que el módulo de ocupación.
_ACTIVE_STATUSES = [
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
]


# --------------------------------------------------------------------------- #
# Costo y presupuesto
# --------------------------------------------------------------------------- #

def _current_period() -> str:
    return date.today().strftime("%Y-%m")


# El cálculo de costo por proveedor/modelo vive en llm_providers.py — cada
# ProviderTurn ya trae su cost_usd calculado con la tabla de precios correcta.


def get_month_spend(db: Session) -> Decimal:
    """Gasto acumulado del mes en curso (0 si no hay fila todavía)."""
    row = (
        db.query(AssistantUsage)
        .filter(AssistantUsage.period == _current_period())
        .first()
    )
    return Decimal(str(row.total_cost_usd)) if row else Decimal(0)


def is_budget_exceeded(db: Session) -> bool:
    return get_month_spend(db) >= Decimal(str(settings.ASSISTANT_MONTHLY_BUDGET_USD))


def _add_spend(db: Session, cost: Decimal) -> None:
    """Suma el costo de una interacción a la fila del mes actual (upsert)."""
    period = _current_period()
    row = db.query(AssistantUsage).filter(AssistantUsage.period == period).first()
    if row is None:
        row = AssistantUsage(period=period, total_cost_usd=cost, request_count=1)
        db.add(row)
    else:
        row.total_cost_usd = Decimal(str(row.total_cost_usd)) + cost
        row.request_count = (row.request_count or 0) + 1
    db.commit()


# --------------------------------------------------------------------------- #
# Definición de tools (JSON Schema). Orden determinista para no romper el caché.
# --------------------------------------------------------------------------- #

TOOLS = [
    {
        "name": "buscar_en_manual",
        "description": (
            "Busca en el manual de usuario del sistema para explicar CÓMO hacer "
            "algo en la interfaz (crear un residente, registrar una toma, generar "
            "cobros, agregar un usuario, etc.). Devuelve las secciones relevantes "
            "del manual con los pasos exactos (a qué menú ir, qué botón pulsar). "
            "Úsalo SIEMPRE que el usuario pregunte cómo hacer, dónde está o cómo "
            "funciona algo del sistema. Pasa palabras clave de la acción; si no "
            "encuentras nada útil, reformula la búsqueda con sinónimos."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Palabras clave de la acción a buscar (p.ej. 'registrar cobro', 'crear residente').",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "buscar_residentes",
        "description": (
            "Busca residentes por nombre o número de cédula. Devuelve una lista "
            "con código, nombre y estado. Úsalo cuando el usuario menciona a una "
            "persona por nombre y necesitas su código o id."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto a buscar (nombre o cédula)."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "detalle_residente",
        "description": (
            "Devuelve los datos de un residente: demográficos básicos y alergias. "
            "Recibe el id numérico del residente (obtenido con buscar_residentes)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resident_id": {"type": "integer", "description": "Id numérico del residente."}
            },
            "required": ["resident_id"],
        },
    },
    {
        "name": "medicamentos_activos",
        "description": (
            "Lista las órdenes de medicamento activas de un residente (medicamento, "
            "dosis, vía, horarios y si es controlado). Recibe el id del residente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resident_id": {"type": "integer", "description": "Id numérico del residente."}
            },
            "required": ["resident_id"],
        },
    },
    {
        "name": "residentes_con_medicamentos_controlados",
        "description": (
            "Devuelve la lista de residentes activos que tienen al menos una orden "
            "de medicamento controlado vigente. No requiere argumentos."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "ocupacion_actual",
        "description": (
            "Devuelve la ocupación actual del centro: capacidad, camas ocupadas y "
            "disponibles, y desglose por estado. No requiere argumentos."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "saldo_financiero",
        "description": (
            "Devuelve el saldo pendiente (cargos menos pagos) de la admisión activa "
            "de un residente. SOLO disponible para usuarios con acceso a finanzas "
            "(admin o recepción); si no, devuelve un error de permiso. Recibe el id "
            "del residente."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "resident_id": {"type": "integer", "description": "Id numérico del residente."}
            },
            "required": ["resident_id"],
        },
    },
]


# --------------------------------------------------------------------------- #
# Ejecución de tools — cada una respeta los permisos del usuario actual.
# --------------------------------------------------------------------------- #

class _ToolExecutor:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def run(self, name: str, args: dict) -> dict:
        handler = getattr(self, f"_t_{name}", None)
        if handler is None:
            return {"error": f"herramienta desconocida: {name}"}
        try:
            return handler(args)
        except PermissionError as e:
            return {"error": str(e)}
        except Exception as e:  # noqa: BLE001 — se traduce a texto para el modelo
            return {"error": f"no se pudo completar la consulta: {e}"}

    # -- helpers de permisos ------------------------------------------------ #

    def _require_module(self, module: Module) -> None:
        if not self.user.has_module(module):
            raise PermissionError(
                "El usuario no tiene permiso para ver esta información."
            )

    def _active_admission(self, resident_id: int) -> Optional[Admission]:
        return (
            self.db.query(Admission)
            .filter(
                Admission.resident_id == resident_id,
                Admission.status.in_(_ACTIVE_STATUSES),
                Admission.is_deleted == False,  # noqa: E712
            )
            .order_by(Admission.admission_date.desc())
            .first()
        )

    # -- tools -------------------------------------------------------------- #

    def _t_buscar_en_manual(self, args: dict) -> dict:
        # El manual es ayuda de uso del sistema; no expone datos de residentes,
        # así que no requiere permiso de módulo.
        from app.services import handbook_search

        results = handbook_search.search(args.get("query", ""), max_results=3)
        if not results:
            return {
                "resultados": [],
                "nota": "No encontré una sección del manual para esa consulta. Reformula con otras palabras clave.",
            }
        return {"resultados": results}

    def _t_buscar_residentes(self, args: dict) -> dict:
        self._require_module(Module.residents)
        page = ResidentService(self.db).list_paginated(
            q=args.get("query"), page=1, page_size=10, show_archived=False
        )
        return {
            "residentes": [
                {
                    "id": r.id,
                    "codigo": r.code,
                    "nombre": f"{r.first_name} {r.last_name}",
                    "cedula": r.id_number,
                }
                for r in page.items
            ],
            "total": page.total,
        }

    def _t_detalle_residente(self, args: dict) -> dict:
        self._require_module(Module.residents)
        r = ResidentService(self.db).get(args["resident_id"])
        return {
            "id": r.id,
            "codigo": r.code,
            "nombre": f"{r.first_name} {r.last_name}",
            "cedula": r.id_number,
            "fecha_nacimiento": r.birthdate.isoformat() if r.birthdate else None,
            "sexo": r.sex.value if r.sex else None,
            "telefono": r.phone_mobile or r.phone_home,
            "alergias": [
                {
                    "sustancia": a.substance,
                    "reaccion": a.reaction,
                    "severidad": a.severity.value if a.severity else None,
                }
                for a in r.allergies
            ],
        }

    def _t_medicamentos_activos(self, args: dict) -> dict:
        # El pase de medicamentos vive bajo el módulo de operaciones.
        self._require_module(Module.operations)
        adm = self._active_admission(args["resident_id"])
        if adm is None:
            return {"medicamentos": [], "nota": "El residente no tiene una admisión activa."}
        from app.models.medication import MedicationOrder, OrderStatus

        orders = (
            self.db.query(MedicationOrder)
            .filter(
                MedicationOrder.admission_id == adm.id,
                MedicationOrder.status == OrderStatus.active,
            )
            .all()
        )
        return {
            "medicamentos": [
                {
                    "medicamento": o.medication.name if o.medication else None,
                    "dosis": o.dose,
                    "via": o.route.value if o.route else None,
                    "tipo_horario": o.schedule_type.value if o.schedule_type else None,
                    "horas": o.times,
                    "controlado": bool(o.is_controlled or (o.medication and o.medication.is_controlled)),
                }
                for o in orders
            ]
        }

    def _t_residentes_con_medicamentos_controlados(self, args: dict) -> dict:
        self._require_module(Module.operations)
        from app.models.medication import Medication, MedicationOrder, OrderStatus
        from app.models.resident import Resident

        rows = (
            self.db.query(Resident, MedicationOrder, Medication)
            .join(Admission, Admission.resident_id == Resident.id)
            .join(MedicationOrder, MedicationOrder.admission_id == Admission.id)
            .join(Medication, Medication.id == MedicationOrder.medication_id)
            .filter(
                Admission.status.in_(_ACTIVE_STATUSES),
                Admission.is_deleted == False,  # noqa: E712
                MedicationOrder.status == OrderStatus.active,
                (MedicationOrder.is_controlled == True) | (Medication.is_controlled == True),  # noqa: E712
            )
            .all()
        )
        by_resident: dict[int, dict] = {}
        for resident, order, med in rows:
            entry = by_resident.setdefault(
                resident.id,
                {"codigo": resident.code, "nombre": f"{resident.first_name} {resident.last_name}", "medicamentos": []},
            )
            entry["medicamentos"].append(med.name)
        return {"residentes": list(by_resident.values()), "total": len(by_resident)}

    def _t_ocupacion_actual(self, args: dict) -> dict:
        self._require_module(Module.operations)
        occ = OccupancyService(self.db).get_occupancy()
        return {
            "capacidad": occ.capacity,
            "ocupadas": occ.occupied,
            "disponibles": occ.available,
            "por_estado": occ.by_status,
        }

    def _t_saldo_financiero(self, args: dict) -> dict:
        self._require_module(Module.finance)
        adm = self._active_admission(args["resident_id"])
        if adm is None:
            return {"nota": "El residente no tiene una admisión activa."}
        account = FinanceService(self.db).get_account(adm.id)
        return {
            "admission_id": adm.id,
            "saldo_pendiente": float(account.balance),
            "total_cargos": float(sum((c.amount for c in account.charges), Decimal(0))),
            "total_pagos": float(sum((p.amount for p in account.payments), Decimal(0))),
        }


# --------------------------------------------------------------------------- #
# System prompt (prefijo estable — se cachea).
# --------------------------------------------------------------------------- #

_SYSTEM_PROMPT = (
    "Eres el asistente de ayuda del expediente clínico de Hogar Zoé, una clínica "
    "de rehabilitación de adicciones en Costa Rica. Ayudas al personal en español, "
    "de forma breve y clara. Atiendes dos tipos de preguntas:\n\n"
    "1. CÓMO USAR EL SISTEMA ('¿cómo creo un residente?', '¿dónde registro un "
    "cobro?', '¿cómo agrego un usuario?'). Para estas SIEMPRE usa la herramienta "
    "buscar_en_manual y responde con los PASOS CONCRETOS que trae el manual.\n"
    "   - EMPIEZA SIEMPRE indicando el módulo del menú lateral donde está la "
    "función. Cada resultado del manual trae un campo 'menu_path' con esa ruta "
    "(p.ej. 'Clínica → Residentes', 'Finanzas → Resumen y morosidad'). Tu primer "
    "paso debe ser navegar ahí. Si el menu_path viene vacío, dedúcelo del "
    "contenido del manual.\n"
    "   - Luego lista los pasos numerados: qué botón pulsar y qué campos llenar. "
    "Ejemplo de formato: '1. En el menú lateral, entra a Clínica → Residentes. "
    "2. Pulsa «+ Nuevo residente». 3. Llena los campos obligatorios (Nombre, "
    "Apellidos). 4. Pulsa «Crear residente».'\n"
    "   - Nunca respondas de forma genérica del tipo 'consulta el manual interno' "
    "o 'contacta a soporte': el manual está a tu disposición, úsalo. Si la primera "
    "búsqueda no trae la sección correcta, reformula con otras palabras clave.\n\n"
    "2. CONSULTAR DATOS del expediente ('¿qué residentes tienen medicamentos "
    "controlados?', '¿cuántas camas hay ocupadas?'). Para estas usa las "
    "herramientas de datos correspondientes.\n\n"
    "Reglas generales:\n"
    "- Eres de SOLO LECTURA: nunca modificas datos ni ofreces hacerlo; solo "
    "explicas cómo hacerlo o consultas información.\n"
    "- Responde únicamente con lo que devuelven las herramientas; no inventes "
    "pasos ni datos.\n"
    "- Refiérete a los residentes por su código y nombre.\n"
    "- Solo puedes ver la información que los permisos del usuario permiten. Si una "
    "herramienta de datos devuelve un error de permiso, explica que no tiene "
    "acceso a esa información, sin revelar el dato. (El manual de uso está "
    "disponible para todos.)\n"
    "- Si no hay información suficiente para responder, dilo con claridad."
)


# --------------------------------------------------------------------------- #
# Loop principal
# --------------------------------------------------------------------------- #

class AssistantService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def _not_configured_reply(self) -> dict:
        return {
            "disabled": True,
            "reason": "not_configured",
            "reply": (
                f"El asistente no está configurado (falta la API key de {_provider_label()}). "
                "Contacta al administrador."
            ),
            "model": _model_label(),
        }

    def chat(self, messages: list[dict]) -> dict:
        """Ejecuta el loop de tool-use y devuelve la respuesta del asistente.

        Devuelve un dict:
          { "reply": str, "cost_usd": float }
        o, si no está configurado / presupuesto agotado, un estado explícito.

        El proveedor (Anthropic, DeepSeek, Gemini o Groq) se resuelve según
        ASSISTANT_PROVIDER; el resto de esta función es idéntico sin importar
        cuál sea.
        """
        provider = build_provider(
            settings.ASSISTANT_PROVIDER,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            anthropic_model=settings.ASSISTANT_MODEL_ANTHROPIC,
            prompt_cache=settings.ASSISTANT_PROMPT_CACHE,
            deepseek_api_key=settings.DEEPSEEK_API_KEY,
            deepseek_model=settings.ASSISTANT_MODEL_DEEPSEEK,
            deepseek_base_url=settings.DEEPSEEK_BASE_URL,
            gemini_api_key=settings.GEMINI_API_KEY,
            gemini_model=settings.ASSISTANT_MODEL_GEMINI,
            groq_api_key=settings.GROQ_API_KEY,
            groq_model=settings.ASSISTANT_MODEL_GROQ,
            groq_base_url=settings.GROQ_BASE_URL,
        )
        if provider is None:
            return self._not_configured_reply()

        if is_budget_exceeded(self.db):
            return {
                "disabled": True,
                "reason": "budget_exceeded",
                "reply": (
                    "El asistente de ayuda alcanzó su límite de uso de este mes. "
                    "Contacta al administrador para reactivarlo."
                ),
                "model": _model_label(),
            }

        executor = _ToolExecutor(self.db, self.user)

        # Historial neutro: turnos de usuario tal cual llegan del frontend.
        history: list[dict] = [{"role": m["role"], "content": m["content"]} for m in messages]
        total_cost = Decimal(0)
        tools_called: list[str] = []
        reply_text = ""

        try:
            for _ in range(_MAX_TOOL_ITERATIONS):
                turn = provider.run_turn(_SYSTEM_PROMPT, TOOLS, history)
                total_cost += turn.cost_usd

                if turn.tool_calls:
                    history.append({"role": "assistant", "raw": turn.raw_assistant_message})
                    calls_and_results: list[tuple[ToolCall, dict]] = []
                    for call in turn.tool_calls:
                        tools_called.append(call.name)
                        result = executor.run(call.name, call.input)
                        calls_and_results.append((call, result))
                    history.append(provider.format_tool_results(calls_and_results))
                    continue

                reply_text = turn.text
                break
        except _PROVIDER_API_ERRORS as e:
            # Error de la API del proveedor (saldo insuficiente, rate limit,
            # clave inválida, etc.). El detalle técnico va a los logs; al
            # usuario se le da un mensaje simple. Se cobra solo lo ya gastado
            # hasta el error (total_cost puede incluir vueltas previas del
            # loop) y no se bloquea el asistente completo: puede reintentar.
            logger.warning("Error del proveedor %s en assistant chat: %s", _provider_label(), e)
            if total_cost > 0:
                _add_spend(self.db, total_cost)
            return {
                "disabled": True,
                "reason": "provider_error",
                "reply": (
                    f"El asistente ({_provider_label()}) no pudo responder en este "
                    "momento. Intenta de nuevo en unos minutos o contacta al "
                    "administrador si el problema persiste."
                ),
                "model": _model_label(),
            }

        # Contabilizar gasto y auditar (misma transacción de auditoría).
        _add_spend(self.db, total_cost)
        self._audit(tools_called)

        return {
            "reply": reply_text or "No obtuve una respuesta.",
            "cost_usd": float(total_cost),
            "model": _model_label(),
        }

    def _audit(self, tools_called: list[str]) -> None:
        entry = AuditLog(
            user_id=self.user.id,
            operation_type=OperationType.update,  # no hay tipo "READ"; se usa el genérico
            table_affected="assistant_query:" + ",".join(sorted(set(tools_called))),
            record_id=None,
        )
        self.db.add(entry)
        self.db.commit()
