"""Capa de abstracción de proveedores de LLM para el asistente "Ask AI".

Problema que resuelve: Anthropic (Claude), DeepSeek, Gemini y Groq exponen tool-use
con formatos de request/response DISTINTOS entre sí. Para poder elegir el
proveedor con una variable de entorno sin duplicar el loop de tool-use, las
tools, los permisos y el cálculo de costo, cada proveedor traduce su formato
nativo a un contrato común (`ProviderTurn` / `ToolCall`) y `AssistantService`
solo habla ese contrato.

Cada proveedor usa el SDK OFICIAL de su API:
  - Anthropic → paquete `anthropic`.
  - DeepSeek  → paquete `openai` apuntando a la base_url de DeepSeek (DeepSeek
    expone una API compatible con el formato de OpenAI; así lo documenta el
    propio proveedor. No es un shim genérico: es el SDK real de la API real
    que DeepSeek decidió exponer).
  - Gemini    → paquete `google-genai` (SDK oficial y vigente de Google; el
    paquete `google-generativeai` está deprecado). Tiene un free tier con
    límites de requests por minuto/día — ver GeminiProvider más abajo.
  - Groq      → paquete `openai` apuntando a la base_url de Groq (misma
    razón que DeepSeek: Groq expone una API compatible con OpenAI). Sirve
    modelos open-weight (Llama, etc.) sobre hardware LPU propio; tiene un
    free tier con límites de requests por minuto/día, igual que Gemini.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional, Protocol


@dataclass
class ToolCall:
    """Una petición del modelo de ejecutar una tool, en formato común."""

    id: str
    name: str
    input: dict


@dataclass
class ProviderTurn:
    """Resultado normalizado de una vuelta del modelo, sea cual sea el proveedor.

    - Si `tool_calls` no está vacío, hay que ejecutar esas tools y continuar el
      loop (igual que un stop_reason == "tool_use" de Claude).
    - Si está vacío, `text` es la respuesta final.
    - `raw_assistant_message` es el mensaje "tal cual lo dio el proveedor", para
      poder re-inyectarlo en el historial en el formato nativo de ESE proveedor
      en la siguiente llamada (cada proveedor tiene su propia forma de
      serializar "el turno anterior del asistente").
    """

    text: str
    tool_calls: list[ToolCall]
    cost_usd: Decimal
    raw_assistant_message: Any
    raw_usage: Optional[dict] = field(default=None)


class LLMProvider(Protocol):
    """Contrato común que implementa cada proveedor.

    `history` es una lista de dicts en formato NEUTRO:
      {"role": "user"|"assistant", "content": str}                (turno normal)
      {"role": "assistant", "raw": <lo que devolvió el proveedor>} (turno con tool_use, eco)
      {"role": "tool_results", "raw": <resultados>, "calls": [...]} (resultados de tools)

    Cada implementación sabe traducir esto a su propio formato de mensajes.
    """

    def run_turn(self, system: str, tools: list[dict], history: list[dict]) -> ProviderTurn:
        ...

    def format_tool_results(self, calls_and_results: list[tuple[ToolCall, dict]]) -> dict:
        """Empaqueta los resultados de tools en el formato que este proveedor
        espera recibir de vuelta, envuelto en un turno neutro `{"role": ..., "raw": ...}`."""
        ...


# --------------------------------------------------------------------------- #
# Anthropic (Claude)
# --------------------------------------------------------------------------- #

class AnthropicProvider:
    def __init__(self, api_key: str, model: str, prompt_cache: bool):
        import anthropic  # import perezoso: no romper el arranque sin la dependencia

        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._prompt_cache = prompt_cache

    def _system_blocks(self, system: str) -> list:
        block: dict = {"type": "text", "text": system}
        if self._prompt_cache:
            block["cache_control"] = {"type": "ephemeral"}
        return [block]

    def _tools_blocks(self, tools: list[dict]) -> list:
        blocks = [dict(t) for t in tools]
        if self._prompt_cache and blocks:
            blocks[-1] = {**blocks[-1], "cache_control": {"type": "ephemeral"}}
        return blocks

    def run_turn(self, system: str, tools: list[dict], history: list[dict]) -> ProviderTurn:
        messages = []
        for turn in history:
            if turn["role"] in ("user", "assistant") and "content" in turn:
                messages.append({"role": turn["role"], "content": turn["content"]})
            elif turn["role"] == "assistant" and "raw" in turn:
                messages.append({"role": "assistant", "content": turn["raw"]})
            elif turn["role"] == "tool_results":
                messages.append({"role": "user", "content": turn["raw"]})

        response = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            system=self._system_blocks(system),
            tools=self._tools_blocks(tools),
            messages=messages,
        )

        cost = _cost_from_generic_usage(
            provider="anthropic",
            model=self._model,
            input_tokens=getattr(response.usage, "input_tokens", 0),
            output_tokens=getattr(response.usage, "output_tokens", 0),
            cache_write_tokens=getattr(response.usage, "cache_creation_input_tokens", 0),
            cache_read_tokens=getattr(response.usage, "cache_read_input_tokens", 0),
        )

        tool_calls = [
            ToolCall(id=b.id, name=b.name, input=b.input or {})
            for b in response.content
            if getattr(b, "type", None) == "tool_use"
        ]
        text = "".join(b.text for b in response.content if getattr(b, "type", None) == "text")

        return ProviderTurn(
            text=text,
            tool_calls=tool_calls,
            cost_usd=cost,
            raw_assistant_message=response.content,
            raw_usage=response.usage.model_dump() if hasattr(response.usage, "model_dump") else None,
        )

    def format_tool_results(self, calls_and_results: list[tuple[ToolCall, dict]]) -> dict:
        import json

        content = [
            {"type": "tool_result", "tool_use_id": call.id, "content": json.dumps(result, ensure_ascii=False)}
            for call, result in calls_and_results
        ]
        return {"role": "tool_results", "raw": content}


# --------------------------------------------------------------------------- #
# DeepSeek / Groq (ambos exponen una API compatible con el formato de OpenAI;
# una sola clase les sirve a los dos, solo cambia base_url + tabla de precios)
# --------------------------------------------------------------------------- #

class DeepSeekProvider:
    def __init__(self, api_key: str, model: str, base_url: str, provider_name: str = "deepseek"):
        import openai  # import perezoso

        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._model = model
        self._provider_name = provider_name

    def _tools_openai_format(self, tools: list[dict]) -> list[dict]:
        # Anthropic: {"name", "description", "input_schema"}
        # OpenAI/DeepSeek: {"type": "function", "function": {"name", "description", "parameters"}}
        return [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["input_schema"],
                },
            }
            for t in tools
        ]

    def run_turn(self, system: str, tools: list[dict], history: list[dict]) -> ProviderTurn:
        messages: list[dict] = [{"role": "system", "content": system}]
        for turn in history:
            if turn["role"] in ("user", "assistant") and "content" in turn:
                messages.append({"role": turn["role"], "content": turn["content"]})
            elif turn["role"] == "assistant" and "raw" in turn:
                messages.append(turn["raw"])  # ya viene en formato de mensaje OpenAI
            elif turn["role"] == "tool_results":
                messages.extend(turn["raw"])  # lista de mensajes role="tool"

        response = self._client.chat.completions.create(
            model=self._model,
            max_tokens=1024,
            messages=messages,
            tools=self._tools_openai_format(tools),
        )

        choice = response.choices[0]
        usage = response.usage

        cost = _cost_from_generic_usage(
            provider=self._provider_name,
            model=self._model,
            input_tokens=getattr(usage, "prompt_tokens", 0),
            output_tokens=getattr(usage, "completion_tokens", 0),
            # DeepSeek reporta tokens de caché en un campo propio (cache hit),
            # con un precio con descuento distinto — ver _cost_from_generic_usage.
            cache_write_tokens=0,
            cache_read_tokens=getattr(
                getattr(usage, "prompt_tokens_details", None), "cached_tokens", 0
            ) or 0,
        )

        tool_calls = []
        if choice.message.tool_calls:
            import json

            for tc in choice.message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, input=args))

        return ProviderTurn(
            text=choice.message.content or "",
            tool_calls=tool_calls,
            cost_usd=cost,
            raw_assistant_message=choice.message.model_dump(exclude_none=True),
            raw_usage=usage.model_dump() if hasattr(usage, "model_dump") else None,
        )

    def format_tool_results(self, calls_and_results: list[tuple[ToolCall, dict]]) -> dict:
        import json

        messages = [
            {"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)}
            for call, result in calls_and_results
        ]
        return {"role": "tool_results", "raw": messages}


# --------------------------------------------------------------------------- #
# Gemini (Google AI Studio) — free tier
# --------------------------------------------------------------------------- #

class GeminiProvider:
    """Usa el modelo gratuito de Gemini (Google AI Studio). Costo $0 dentro del
    free tier; si se excede el límite de requests, la API devuelve un 429 que
    `AssistantService` ya sabe traducir a un mensaje de "intenta más tarde"
    (mismo manejo que un error de cualquier otro proveedor)."""

    def __init__(self, api_key: str, model: str):
        from google import genai  # import perezoso

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def _tools_gemini_format(self, tools: list[dict]) -> list:
        from google.genai import types

        # `parameters_json_schema` acepta JSON Schema plano tal cual —
        # exactamente el formato en que ya están definidas TOOLS.
        declarations = [
            types.FunctionDeclaration(
                name=t["name"],
                description=t["description"],
                parameters_json_schema=t["input_schema"],
            )
            for t in tools
        ]
        return [types.Tool(function_declarations=declarations)]

    def run_turn(self, system: str, tools: list[dict], history: list[dict]) -> ProviderTurn:
        from google.genai import types

        contents = []
        for turn in history:
            if turn["role"] == "user" and "content" in turn:
                contents.append(types.Content(role="user", parts=[types.Part(text=turn["content"])]))
            elif turn["role"] == "assistant" and "content" in turn:
                contents.append(types.Content(role="model", parts=[types.Part(text=turn["content"])]))
            elif turn["role"] == "assistant" and "raw" in turn:
                contents.append(turn["raw"])  # Content completo devuelto por Gemini (con function_call)
            elif turn["role"] == "tool_results":
                contents.append(turn["raw"])  # Content(role="user", parts=[function_response, ...])

        response = self._client.models.generate_content(
            model=self._model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system,
                tools=self._tools_gemini_format(tools),
            ),
        )

        usage = response.usage_metadata
        cost = _cost_from_generic_usage(
            provider="gemini",
            model=self._model,
            input_tokens=getattr(usage, "prompt_token_count", 0) or 0,
            output_tokens=getattr(usage, "candidates_token_count", 0) or 0,
            cache_write_tokens=0,
            cache_read_tokens=getattr(usage, "cached_content_token_count", 0) or 0,
        )

        function_calls = response.function_calls or []
        tool_calls = [
            ToolCall(id=fc.id or fc.name, name=fc.name, input=fc.args or {})
            for fc in function_calls
        ]

        # raw_assistant_message es el Content completo del primer candidato,
        # para poder re-inyectarlo tal cual (con sus function_call parts) en
        # la siguiente vuelta del loop.
        raw_content = response.candidates[0].content if response.candidates else None

        return ProviderTurn(
            text=response.text or "",
            tool_calls=tool_calls,
            cost_usd=cost,
            raw_assistant_message=raw_content,
            raw_usage=usage.model_dump() if usage and hasattr(usage, "model_dump") else None,
        )

    def format_tool_results(self, calls_and_results: list[tuple[ToolCall, dict]]) -> dict:
        from google.genai import types

        parts = [
            types.Part(
                function_response=types.FunctionResponse(
                    id=call.id, name=call.name, response=result
                )
            )
            for call, result in calls_and_results
        ]
        return {"role": "tool_results", "raw": types.Content(role="user", parts=parts)}


# --------------------------------------------------------------------------- #
# Precios (USD por millón de tokens) por proveedor + modelo.
# --------------------------------------------------------------------------- #

_PRICES_PER_MTOK = {
    "anthropic": {
        "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
        "claude-opus-4-8": {"input": 5.00, "output": 25.00},
        "claude-sonnet-5": {"input": 3.00, "output": 15.00},
    },
    "deepseek": {
        # Precios de lista de DeepSeek (USD/MTok); verificar en
        # https://platform.deepseek.com/pricing si cambian.
        "deepseek-chat": {"input": 0.28, "output": 0.42, "cache_read": 0.028},
        "deepseek-reasoner": {"input": 0.28, "output": 0.42, "cache_read": 0.028},
    },
    "gemini": {
        # Free tier de Google AI Studio: $0 por token, limitado por requests
        # por minuto/día (no por gasto). El tope de gasto mensual del
        # asistente sigue funcionando, pero con Gemini gratis casi nunca se
        # alcanzará por costo — el límite real es el rate limit del free tier,
        # que la API devuelve como 429 (ver GeminiProvider / manejo de error).
        "gemini-2.0-flash": {"input": 0.0, "output": 0.0},
        "gemini-2.5-flash": {"input": 0.0, "output": 0.0},
        "gemini-flash-latest": {"input": 0.0, "output": 0.0},
    },
    "groq": {
        # Free tier de Groq: $0 por token, limitado por requests por
        # minuto/día (igual que Gemini). Ver GroqProvider / build_provider.
        "llama-3.3-70b-versatile": {"input": 0.0, "output": 0.0},
        "llama-3.1-8b-instant": {"input": 0.0, "output": 0.0},
    },
}
_ANTHROPIC_CACHE_WRITE_FACTOR = 1.25
_ANTHROPIC_CACHE_READ_FACTOR = 0.10


def _cost_from_generic_usage(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_write_tokens: int,
    cache_read_tokens: int,
) -> Decimal:
    prices = _PRICES_PER_MTOK.get(provider, {}).get(model)
    if prices is None:
        # Proveedor/modelo sin tabla de precios: no se puede calcular con
        # certeza. Se reporta 0 en vez de adivinar un precio incorrecto.
        return Decimal(0)

    input_price = Decimal(str(prices["input"]))
    output_price = Decimal(str(prices["output"]))
    per_tok_in = input_price / Decimal(1_000_000)
    per_tok_out = output_price / Decimal(1_000_000)

    cost = Decimal(input_tokens) * per_tok_in + Decimal(output_tokens) * per_tok_out

    if provider == "anthropic":
        cost += Decimal(cache_write_tokens) * per_tok_in * Decimal(str(_ANTHROPIC_CACHE_WRITE_FACTOR))
        cost += Decimal(cache_read_tokens) * per_tok_in * Decimal(str(_ANTHROPIC_CACHE_READ_FACTOR))
    elif provider == "deepseek" and cache_read_tokens:
        # DeepSeek cachea automáticamente (sin cache_control explícito) y
        # cobra los tokens de caché a un precio propio, más bajo que el de
        # entrada normal. Se resta el tramo de entrada normal ya sumado
        # arriba y se recalcula ese tramo al precio de caché.
        cache_read_price = Decimal(str(prices.get("cache_read", prices["input"])))
        per_tok_cache = cache_read_price / Decimal(1_000_000)
        cost -= Decimal(cache_read_tokens) * per_tok_in
        cost += Decimal(cache_read_tokens) * per_tok_cache

    return cost


def build_provider(
    provider_name: str,
    *,
    anthropic_api_key: Optional[str],
    anthropic_model: str,
    prompt_cache: bool,
    deepseek_api_key: Optional[str],
    deepseek_model: str,
    deepseek_base_url: str,
    gemini_api_key: Optional[str] = None,
    gemini_model: str = "gemini-2.0-flash",
    groq_api_key: Optional[str] = None,
    groq_model: str = "llama-3.3-70b-versatile",
    groq_base_url: str = "https://api.groq.com/openai/v1",
) -> Optional[LLMProvider]:
    """Construye el proveedor configurado, o None si falta su API key."""
    if provider_name == "deepseek":
        if not deepseek_api_key:
            return None
        return DeepSeekProvider(api_key=deepseek_api_key, model=deepseek_model, base_url=deepseek_base_url)

    if provider_name == "gemini":
        if not gemini_api_key:
            return None
        return GeminiProvider(api_key=gemini_api_key, model=gemini_model)

    if provider_name == "groq":
        if not groq_api_key:
            return None
        # Groq expone una API compatible con OpenAI, igual que DeepSeek:
        # se reutiliza la misma clase con otro base_url y tabla de precios.
        return DeepSeekProvider(
            api_key=groq_api_key, model=groq_model, base_url=groq_base_url, provider_name="groq"
        )

    # Por defecto / "anthropic"
    if not anthropic_api_key:
        return None
    return AnthropicProvider(api_key=anthropic_api_key, model=anthropic_model, prompt_cache=prompt_cache)
