"""
Router para el módulo de Entrega de turno (Shift Handover). Routers delgados:
toda la lógica vive en app/services/handover_service.py.

Rutas bajo /shift-handovers:
  GET  /shift-handovers                   — get_or_create handover (?date=&shift=)
  GET  /shift-handovers/{id}/auto-summary — recomputa y devuelve el auto-resumen
  POST /shift-handovers/{id}/close        — congela auto_summary, status=closed
  POST /shift-handovers/{id}/receive      — status=received (400 si no está closed)
  GET  /shift-handovers/{id}/incidents    — lista incidentes del turno
  POST /shift-handovers/{id}/incidents    — crea incidente
  GET  /shift-handovers/{id}/tasks        — lista tareas del turno
  POST /shift-handovers/{id}/tasks        — crea tarea

Rutas bajo /shift-tasks:
  PATCH /shift-tasks/{id}                 — editar/marcar done
"""

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Shift
from app.models.user import User
from app.schemas.handover import (
    AutoSummaryOut,
    ShiftHandoverClose,
    ShiftHandoverOut,
    ShiftIncidentCreate,
    ShiftIncidentOut,
    ShiftTaskCreate,
    ShiftTaskOut,
    ShiftTaskPatch,
)
from app.services.handover_service import HandoverService

# ─── Router principal (/shift-handovers) ─────────────────────────────────────
router = APIRouter()

# ─── Router secundario (/shift-tasks) ────────────────────────────────────────
tasks_router = APIRouter()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _parse_date(date_str: Optional[str]) -> date_type:
    if date_str is None:
        return date_type.today()
    try:
        return date_type.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(status_code=422, detail="Formato de fecha inválido. Use YYYY-MM-DD.")


def _parse_shift(shift_str: Optional[str]) -> Shift:
    if shift_str is None:
        return Shift.morning
    try:
        return Shift(shift_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Turno inválido. Valores permitidos: {[s.value for s in Shift]}",
        )


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.get("", response_model=ShiftHandoverOut)
def get_or_create_handover(
    target_date: Optional[str] = Query(None, alias="date"),
    shift: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Obtiene (o crea en estado open) el handover para (date, shift) y devuelve
    el auto-resumen en vivo si está abierto, o el snapshot congelado si está cerrado."""
    return HandoverService(db).get_handover(_parse_date(target_date), _parse_shift(shift))


@router.get("/{handover_id}/auto-summary", response_model=AutoSummaryOut)
def get_auto_summary(
    handover_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Recomputa y devuelve el auto-resumen del turno."""
    svc = HandoverService(db)
    handover = svc.get_handover_by_id(handover_id)
    summary = svc.compute_auto_summary(handover.date, handover.shift)
    return AutoSummaryOut(date=handover.date, shift=handover.shift, summary=summary)


@router.post("/{handover_id}/close", response_model=ShiftHandoverOut)
def close_handover(
    handover_id: int,
    payload: Optional[ShiftHandoverClose] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cierra el handover: congela el auto_summary, setea closed_by/closed_at, status=closed."""
    notes = payload.notes if payload else None
    return HandoverService(db).close(handover_id, current_user.id, notes)


@router.post("/{handover_id}/receive", response_model=ShiftHandoverOut)
def receive_handover(
    handover_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marca el handover como recibido. Solo funciona si está 'closed' (si no → 400)."""
    return HandoverService(db).receive(handover_id, current_user.id)


@router.get("/{handover_id}/incidents", response_model=List[ShiftIncidentOut])
def list_incidents(
    handover_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista todos los incidentes de un handover."""
    return HandoverService(db).list_incidents(handover_id)


@router.post("/{handover_id}/incidents", response_model=ShiftIncidentOut, status_code=201)
def create_incident(
    handover_id: int,
    data: ShiftIncidentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea un incidente para el handover."""
    return HandoverService(db).create_incident(handover_id, data, current_user.id)


@router.get("/{handover_id}/tasks", response_model=List[ShiftTaskOut])
def list_tasks(
    handover_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lista todas las tareas de un handover."""
    return HandoverService(db).list_tasks(handover_id)


@router.post("/{handover_id}/tasks", response_model=ShiftTaskOut, status_code=201)
def create_task(
    handover_id: int,
    data: ShiftTaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una tarea para el handover."""
    return HandoverService(db).create_task(handover_id, data, current_user.id)


@tasks_router.patch("/{task_id}", response_model=ShiftTaskOut)
def patch_task(
    task_id: int,
    data: ShiftTaskPatch,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edita una tarea. Si is_done=True se setea done_by_user_id=current_user."""
    return HandoverService(db).patch_task(task_id, data, current_user.id)
