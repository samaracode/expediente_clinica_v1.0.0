"""
Router para el módulo de Asistencia (presencia física).

Rutas:
  GET  /attendance/roll-call          — roster pre-llenado (?date=&shift=)
  POST /attendance/roll-call          — guardar/confirmar pase (upsert)
  GET  /attendance/today              — resumen de conteo del día (?date=)
  GET  /admissions/{id}/attendance    — historial por residente
"""

from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.attendance import Shift
from app.models.user import User
from app.schemas.attendance import (
    AttendanceSummaryOut,
    EntryOut,
    RollCallCreate,
    RollCallOut,
    RosterOut,
)
from app.services.attendance_service import AttendanceService

# ─── Router de nivel centro (/attendance) ───────────────────────────────────
attendance_router = APIRouter()


@attendance_router.get("/roll-call", response_model=RosterOut)
def get_roster(
    target_date: Optional[str] = Query(None, alias="date"),
    shift: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Roster pre-llenado para una fecha/turno.
    Si ya existe un pase guardado, lo devuelve; si no, calcula el estado esperado.
    """
    parsed_date = _parse_date(target_date)
    parsed_shift = _parse_shift(shift)
    return AttendanceService(db).get_roster(parsed_date, parsed_shift)


@attendance_router.post("/roll-call", response_model=RollCallOut, status_code=201)
def confirm_roll_call(
    data: RollCallCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Guarda/confirma un pase de lista.
    Si ya existe uno para (date, shift), lo actualiza (upsert).
    """
    return AttendanceService(db).confirm_roll_call(data, current_user.id)


@attendance_router.get("/today", response_model=AttendanceSummaryOut)
def today_summary(
    target_date: Optional[str] = Query(None, alias="date"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Resumen de conteo del día.
    Usa el último roll-call del día si existe, o el estado esperado si no hay.
    """
    parsed_date = _parse_date(target_date) if target_date else None
    return AttendanceService(db).get_today_summary(parsed_date)


# ─── Router bajo /admissions ─────────────────────────────────────────────────
admissions_attendance_router = APIRouter()


@admissions_attendance_router.get(
    "/{admission_id}/attendance",
    response_model=List[EntryOut],
)
def get_admission_attendance(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Historial de entradas de asistencia de un residente."""
    return AttendanceService(db).get_admission_history(admission_id)


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
        return Shift.morning  # default
    try:
        return Shift(shift_str)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Turno inválido. Valores permitidos: {[s.value for s in Shift]}",
        )
