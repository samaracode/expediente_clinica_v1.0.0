"""
Schemas Pydantic v2 para el módulo de Asistencia.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.attendance import PresenceStatus, Shift


# ---------------------------------------------------------------------------
# AttendanceRollCall
# ---------------------------------------------------------------------------

class RollCallCreate(BaseModel):
    """Payload para confirmar/guardar un pase de lista (POST)."""
    date: date
    shift: Shift
    notes: Optional[str] = None
    entries: List["EntryIn"]


class EntryIn(BaseModel):
    """Una entrada dentro del POST de un pase."""
    admission_id: int
    expected_status: PresenceStatus
    actual_status: PresenceStatus
    note: Optional[str] = None


class RollCallOut(BaseModel):
    """Respuesta de un pase guardado."""
    id: int
    date: date
    shift: Shift
    conducted_by_user_id: Optional[int] = None
    conducted_at: Optional[datetime] = None
    notes: Optional[str] = None
    entries: List["EntryOut"] = []

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# AttendanceEntry
# ---------------------------------------------------------------------------

class EntryOut(BaseModel):
    id: int
    roll_call_id: int
    admission_id: int
    expected_status: PresenceStatus
    actual_status: PresenceStatus
    note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Roster pre-llenado (GET sin persistir)
# ---------------------------------------------------------------------------

class RosterEntryOut(BaseModel):
    """Entrada del roster pre-llenado: estado calculado, sin id de DB."""
    admission_id: int
    resident_id: int
    resident_name: str
    expected_status: PresenceStatus
    # Si ya fue confirmado, vendrá el actual_status guardado; si no, None.
    actual_status: Optional[PresenceStatus] = None
    note: Optional[str] = None
    entry_id: Optional[int] = None  # id de AttendanceEntry si ya existe


class RosterOut(BaseModel):
    """Respuesta del GET /attendance/roll-call."""
    date: date
    shift: Shift
    roll_call_id: Optional[int] = None  # None si aún no existe en DB
    conducted_by_user_id: Optional[int] = None
    conducted_at: Optional[datetime] = None
    notes: Optional[str] = None
    entries: List[RosterEntryOut] = []


# ---------------------------------------------------------------------------
# Resumen del día (/attendance/today)
# ---------------------------------------------------------------------------

class AttendanceSummaryOut(BaseModel):
    date: date
    source: str  # "roll_call" si hay pase guardado, "expected" si es calculado
    total: int
    present: int
    on_pass: int
    external_appointment: int
    hospitalized: int
    absent_without_leave: int
    discharged: int


# Actualizar forward references
RollCallOut.model_rebuild()
RosterOut.model_rebuild()
