from typing import Any, List, Optional
from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict

from app.models.medication import (
    AllergySeverity,
    AdministrationStatus,
    MedicationRoute,
    OrderStatus,
    ScheduleType,
)


# ---------------------------------------------------------------------------
# Extra schemas para la capa de API (no estaban en los base schemas)
# ---------------------------------------------------------------------------

class MedicationOrderPatch(BaseModel):
    """Campos actualizables de una orden (PATCH parcial)."""
    dose: Optional[str] = None
    route: Optional[MedicationRoute] = None
    schedule_type: Optional[ScheduleType] = None
    times: Optional[List[str]] = None
    frequency_text: Optional[str] = None
    prn_reason: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prescribed_by_external: Optional[str] = None
    prescriber_institution: Optional[str] = None
    transcribed_by_user_id: Optional[int] = None
    receta_file_id: Optional[int] = None
    is_controlled: Optional[bool] = None
    status: Optional[OrderStatus] = None
    notes: Optional[str] = None


class AdministrationRecord(BaseModel):
    """Payload para marcar una toma (taken / refused / omitted)."""
    status: AdministrationStatus
    administered_at: Optional[datetime] = None
    witness_user_id: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


class PRNRecord(BaseModel):
    """Payload para registrar una toma PRN ad-hoc."""
    reason: str  # obligatorio por regla de negocio
    administered_at: Optional[datetime] = None
    witness_user_id: Optional[int] = None
    notes: Optional[str] = None


class MedTimeSlotUpdate(BaseModel):
    """Actualización de una franja horaria (PUT completo de la lista)."""
    id: Optional[int] = None
    label: str
    time: time
    sort_order: int = 0


class MedicationAdministrationOut(BaseModel):
    id: int
    order_id: int
    admission_id: int
    scheduled_at: Optional[datetime] = None
    status: AdministrationStatus
    administered_at: Optional[datetime] = None
    administered_by_user_id: Optional[int] = None
    witness_user_id: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    is_overdue: bool = False

    model_config = ConfigDict(from_attributes=True)


class AllergyBrief(BaseModel):
    """Versión resumida de una alergia para el pase del día."""
    id: int
    substance: str
    severity: Optional[AllergySeverity] = None

    model_config = ConfigDict(from_attributes=True)


class PassEntryOut(BaseModel):
    """Una entrada del pase del día (toma + contexto del residente)."""
    administration_id: int
    order_id: int
    admission_id: int
    resident_id: int
    resident_name: str
    medication_name: str
    dose: str
    route: MedicationRoute
    is_controlled: bool
    scheduled_at: Optional[datetime] = None
    slot_label: Optional[str] = None
    status: AdministrationStatus
    administered_at: Optional[datetime] = None
    administered_by_user_id: Optional[int] = None
    witness_user_id: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    is_overdue: bool = False
    allergies: List["AllergyBrief"] = []


class DailyPassOut(BaseModel):
    """Respuesta del endpoint GET /medications/pass."""
    date: date
    entries: List[PassEntryOut]


# ---------------------------------------------------------------------------
# Medication (catálogo)
# ---------------------------------------------------------------------------

class MedicationCreate(BaseModel):
    name: str
    form: Optional[str] = None
    strength: Optional[str] = None
    is_controlled: bool = False
    notes: Optional[str] = None


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    form: Optional[str] = None
    strength: Optional[str] = None
    is_controlled: Optional[bool] = None
    notes: Optional[str] = None


class MedicationOut(BaseModel):
    id: int
    name: str
    form: Optional[str] = None
    strength: Optional[str] = None
    is_controlled: bool
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# MedicationOrder
# ---------------------------------------------------------------------------

class MedicationOrderCreate(BaseModel):
    admission_id: int
    medication_id: int
    dose: str
    route: MedicationRoute
    schedule_type: ScheduleType
    times: Optional[List[str]] = None
    frequency_text: Optional[str] = None
    prn_reason: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    prescribed_by_external: Optional[str] = None
    prescriber_institution: Optional[str] = None
    transcribed_by_user_id: Optional[int] = None
    receta_file_id: Optional[int] = None
    is_controlled: bool = False
    notes: Optional[str] = None


class MedicationOrderOut(BaseModel):
    id: int
    admission_id: int
    medication_id: int
    dose: str
    route: MedicationRoute
    schedule_type: ScheduleType
    times: Optional[Any] = None
    frequency_text: Optional[str] = None
    prn_reason: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    prescribed_by_external: Optional[str] = None
    prescriber_institution: Optional[str] = None
    transcribed_by_user_id: Optional[int] = None
    receta_file_id: Optional[int] = None
    is_controlled: bool
    status: OrderStatus
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# MedicationAdministration
# ---------------------------------------------------------------------------

class MedicationAdministrationCreate(BaseModel):
    order_id: int
    admission_id: int
    scheduled_at: Optional[datetime] = None
    status: AdministrationStatus = AdministrationStatus.pending
    administered_at: Optional[datetime] = None
    administered_by_user_id: Optional[int] = None
    witness_user_id: Optional[int] = None
    reason: Optional[str] = None
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# MedTimeSlot
# ---------------------------------------------------------------------------

class MedTimeSlotCreate(BaseModel):
    label: str
    time: time
    sort_order: int = 0


class MedTimeSlotOut(BaseModel):
    id: int
    label: str
    time: time
    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# ResidentAllergy
# ---------------------------------------------------------------------------

class ResidentAllergyCreate(BaseModel):
    resident_id: int
    substance: str
    reaction: Optional[str] = None
    severity: Optional[AllergySeverity] = None


class ResidentAllergyOut(BaseModel):
    id: int
    resident_id: int
    substance: str
    reaction: Optional[str] = None
    severity: Optional[AllergySeverity] = None

    model_config = ConfigDict(from_attributes=True)
