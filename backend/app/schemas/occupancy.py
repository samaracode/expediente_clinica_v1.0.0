"""
Schemas Pydantic v2 para el módulo de Ocupación + Lista de espera.
"""

from datetime import date, datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.occupancy import WaitlistStatus


# ---------------------------------------------------------------------------
# Ocupación
# ---------------------------------------------------------------------------

class OccupancyOut(BaseModel):
    capacity: int
    occupied: int
    available: int
    by_status: Dict[str, int]


# ---------------------------------------------------------------------------
# Capacity
# ---------------------------------------------------------------------------

class CapacityOut(BaseModel):
    capacity: int


class CapacityIn(BaseModel):
    capacity: int

    @field_validator("capacity")
    @classmethod
    def must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("La capacidad debe ser un entero positivo (> 0).")
        return v


# ---------------------------------------------------------------------------
# Waitlist
# ---------------------------------------------------------------------------

class WaitlistEntryCreate(BaseModel):
    full_name: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    requested_at: Optional[date] = None
    referred_by: Optional[str] = None
    notes: Optional[str] = None


class WaitlistEntryPatch(BaseModel):
    full_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    requested_at: Optional[date] = None
    referred_by: Optional[str] = None
    status: Optional[WaitlistStatus] = None
    notes: Optional[str] = None


class WaitlistEntryOut(BaseModel):
    id: int
    full_name: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    requested_at: Optional[date] = None
    referred_by: Optional[str] = None
    status: WaitlistStatus
    notes: Optional[str] = None
    created_by_user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
