"""Router del asistente "Ask AI" — consulta de datos por lenguaje natural.

Ruta:
  POST /assistant/chat — recibe el historial de la conversación y devuelve la
                         respuesta del asistente.

Cualquier usuario autenticado puede usarlo; qué datos ve el asistente depende de
los permisos por módulo del usuario (las tools los validan internamente).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter()


@router.post("/chat", response_model=AssistantChatResponse)
def chat(
    body: AssistantChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    result = AssistantService(db, current_user).chat(messages)
    return AssistantChatResponse(**result)
