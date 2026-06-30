"""
Schemas Pydantic v2 para el módulo de Entrega de turno (shift handover).
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict

from app.models.attendance import Shift
from app.models.handover import HandoverStatus, IncidentSeverity


# ---------------------------------------------------------------------------
# ShiftHandover
# ---------------------------------------------------------------------------

class ShiftHandoverOut(BaseModel):
    """Respuesta de un shift handover."""
    id: int
    date: date
    shift: Shift
    auto_summary: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    closed_by_user_id: Optional[int] = None
    closed_at: Optional[datetime] = None
    received_by_user_id: Optional[int] = None
    received_at: Optional[datetime] = None
    status: HandoverStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ShiftHandoverClose(BaseModel):
    """Payload opcional para cerrar un handover (POST /close)."""
    notes: Optional[str] = None


class ShiftHandoverReceive(BaseModel):
    """Payload opcional para recibir un handover (POST /receive)."""
    pass


# ---------------------------------------------------------------------------
# ShiftIncident
# ---------------------------------------------------------------------------

class ShiftIncidentCreate(BaseModel):
    """Payload para crear un incidente (POST /incidents)."""
    admission_id: Optional[int] = None
    type: str
    severity: IncidentSeverity
    description: str
    action_taken: Optional[str] = None
    reported_by_user_id: Optional[int] = None


class ShiftIncidentOut(BaseModel):
    """Respuesta de un incidente."""
    id: int
    handover_id: int
    admission_id: Optional[int] = None
    type: str
    severity: IncidentSeverity
    description: str
    action_taken: Optional[str] = None
    reported_by_user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# ShiftTask
# ---------------------------------------------------------------------------

class ShiftTaskCreate(BaseModel):
    """Payload para crear una tarea (POST /tasks)."""
    related_admission_id: Optional[int] = None
    description: str
    due_at: Optional[datetime] = None


class ShiftTaskPatch(BaseModel):
    """Payload para editar/marcar done una tarea (PATCH /shift-tasks/{id})."""
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    is_done: Optional[bool] = None
    done_by_user_id: Optional[int] = None


class ShiftTaskOut(BaseModel):
    """Respuesta de una tarea."""
    id: int
    handover_id: int
    related_admission_id: Optional[int] = None
    description: str
    due_at: Optional[datetime] = None
    is_done: bool
    done_by_user_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Auto-summary (solo output, estructura interna)
# ---------------------------------------------------------------------------

class AutoSummaryOut(BaseModel):
    """Respuesta del endpoint de auto-resumen."""
    date: date
    shift: Shift
    summary: Dict[str, Any]
