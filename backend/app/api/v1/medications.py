"""
Router para el módulo de Medicamentos (MAR).

Rutas cubiertas:
  GET  /medications                                   — catálogo
  POST /medications                                   — agregar al catálogo (admin)
  PUT  /medications/{id}                              — editar catálogo (admin)
  GET  /medications/pass                              — pase del día center-wide
  GET  /admissions/{admission_id}/medication-orders   — órdenes por admisión
  POST /admissions/{admission_id}/medication-orders   — crear orden
  PATCH /medication-orders/{order_id}                 — editar/suspender/finalizar orden
  POST /medication-administrations/{adm_id}/record    — marcar toma
  POST /admissions/{admission_id}/medication-orders/{order_id}/prn — toma PRN

Nota de permisos: las rutas operativas (órdenes, administraciones, PRN, pase del
día, listar catálogo) requieren el módulo Operación (ModuleRequired) — se
mantiene "designación por turno": cualquiera con el módulo puede actuar, el
sistema solo registra QUIÉN realizó cada acción. La escritura del CATÁLOGO
(POST /medications) es admin-only (ADR/plan: el catálogo lo gestiona el
administrador, no se crea al vuelo al prescribir).
"""

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import ModuleRequired, RoleRequired
from app.db.session import get_db
from app.models.user import Module, User
from app.schemas.medication import (
    AdministrationRecord,
    DailyPassOut,
    MedicationAdministrationOut,
    MedicationCreate,
    MedicationOrderCreate,
    MedicationOrderOut,
    MedicationOrderPatch,
    MedicationOut,
    MedicationUpdate,
    PRNRecord,
)
from app.services.medication_service import (
    AdministrationService,
    DailyPassService,
    MedicationCatalogService,
    MedicationOrderService,
    MedTimeSlotsService,
)

# ─── Router para rutas bajo /medications ────────────────────────────────────
medications_router = APIRouter()
_role = ModuleRequired(Module.operations)
_admin_only = RoleRequired(["admin"])


@medications_router.get("", response_model=List[MedicationOut])
def list_medications(
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    return MedicationCatalogService(db).list()


@medications_router.post("", response_model=MedicationOut, status_code=201)
def create_medication(
    data: MedicationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    return MedicationCatalogService(db).create(data)


@medications_router.put("/{medication_id}", response_model=MedicationOut)
def update_medication(
    medication_id: int,
    data: MedicationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    return MedicationCatalogService(db).update(medication_id, data)


@medications_router.get("/pass", response_model=DailyPassOut)
def daily_pass(
    target_date: Optional[str] = Query(None, alias="date"),
    slot_id: Optional[int] = Query(None, alias="slot"),
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """
    Pase del día center-wide.

    - ?date=YYYY-MM-DD  (default: hoy)
    - ?slot=<slot_id>   (opcional, filtra por franja horaria)

    Genera lazily las tomas pending faltantes antes de responder.
    Incluye flag is_overdue en cada toma.
    """
    if target_date:
        try:
            parsed = date_type.fromisoformat(target_date)
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(status_code=422, detail="Formato de fecha inválido. Use YYYY-MM-DD.")
    else:
        from datetime import date
        parsed = date.today()

    return DailyPassService(db).get_pass(parsed, slot_id)


# ─── Router para rutas bajo /admissions ──────────────────────────────────────
admissions_medication_router = APIRouter()


@admissions_medication_router.get(
    "/{admission_id}/medication-orders",
    response_model=List[MedicationOrderOut],
)
def list_orders(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    return MedicationOrderService(db).list_by_admission(admission_id)


@admissions_medication_router.post(
    "/{admission_id}/medication-orders",
    response_model=MedicationOrderOut,
    status_code=201,
)
def create_order(
    admission_id: int,
    data: MedicationOrderCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    return MedicationOrderService(db).create(admission_id, data)


@admissions_medication_router.post(
    "/{admission_id}/medication-orders/{order_id}/prn",
    response_model=MedicationAdministrationOut,
    status_code=201,
)
def record_prn(
    admission_id: int,
    order_id: int,
    data: PRNRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(_role),
):
    return AdministrationService(db).record_prn(admission_id, order_id, data, current_user.id)


# ─── Router para rutas bajo /medication-orders ───────────────────────────────
orders_router = APIRouter()


@orders_router.get(
    "/{order_id}/administrations",
    response_model=List[MedicationAdministrationOut],
)
def list_order_administrations(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """
    Historial de tomas de una orden específica, ordenadas por fecha (más reciente primero).
    Devuelve 404 si la orden no existe.
    """
    return MedicationOrderService(db).list_administrations_by_order(order_id)


@orders_router.patch("/{order_id}", response_model=MedicationOrderOut)
def patch_order(
    order_id: int,
    data: MedicationOrderPatch,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    return MedicationOrderService(db).patch(order_id, data)


# ─── Router para rutas bajo /medication-administrations ──────────────────────
administrations_router = APIRouter()


@administrations_router.post(
    "/{adm_id}/record",
    response_model=MedicationAdministrationOut,
)
def record_administration(
    adm_id: int,
    data: AdministrationRecord,
    db: Session = Depends(get_db),
    current_user: User = Depends(_role),
):
    return AdministrationService(db).record(adm_id, data, current_user.id)
