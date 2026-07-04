from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class AssistantMessage(BaseModel):
    """Un turno de la conversación. `content` es texto plano (v1 sin imágenes)."""

    role: Literal["user", "assistant"]
    content: str


class AssistantChatRequest(BaseModel):
    messages: List[AssistantMessage] = Field(..., min_length=1)


class AssistantChatResponse(BaseModel):
    reply: str
    # Presente cuando el asistente está desactivado (no configurado o tope de
    # gasto alcanzado); el frontend lo usa para mostrar el mensaje adecuado.
    disabled: bool = False
    reason: Optional[str] = None
    # Costo aproximado de esta pregunta en USD (informativo; None si desactivado).
    cost_usd: Optional[float] = None
