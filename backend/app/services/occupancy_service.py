"""
Capa de lógica de negocio para el módulo de Ocupación + Lista de espera.

Definición de "admisión activa" (ocupa cupo):
  status en {consents_pending, assessment_in_progress, treatment_active}.
  `intake_pending`, `discharged` y `abandoned` NO cuentan.

Capacidad:
  Guardada en clinic_settings con key='capacity' (valor int serializado a str).
  Default = 24 si la clave no existe en la tabla.
"""

from datetime import date as date_type
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.admission import Admission, AdmissionStatus
from app.models.occupancy import ClinicSetting, WaitlistEntry, WaitlistStatus
from app.schemas.occupancy import (
    CapacityIn,
    CapacityOut,
    OccupancyOut,
    WaitlistEntryCreate,
    WaitlistEntryOut,
    WaitlistEntryPatch,
)

# Clave usada en clinic_settings para la capacidad del centro
CAPACITY_KEY = "capacity"
DEFAULT_CAPACITY = 24

# Statuses que cuentan como "admisión activa" (ocupa cupo)
ACTIVE_STATUSES = {
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
}


def _get_capacity_value(db: Session) -> int:
    row = db.query(ClinicSetting).filter(ClinicSetting.key == CAPACITY_KEY).first()
    if row is None:
        return DEFAULT_CAPACITY
    return int(row.value)


class OccupancyService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # GET /occupancy
    # ------------------------------------------------------------------

    def get_occupancy(self) -> OccupancyOut:
        """
        Calcula ocupación actual:
        - occupied = cantidad de admisiones con status activo
        - by_status = desglose por cada status activo
        - available = capacity - occupied
        """
        capacity = _get_capacity_value(self.db)

        # Contar admisiones por status activo
        active_admissions = (
            self.db.query(Admission.status, Admission.id)
            .filter(Admission.status.in_(list(ACTIVE_STATUSES)))
            .filter(Admission.is_deleted == False)  # noqa: E712
            .all()
        )

        by_status: dict = {s.value: 0 for s in ACTIVE_STATUSES}
        for row in active_admissions:
            by_status[row.status.value] = by_status.get(row.status.value, 0) + 1

        occupied = len(active_admissions)
        available = max(capacity - occupied, 0)

        return OccupancyOut(
            capacity=capacity,
            occupied=occupied,
            available=available,
            by_status=by_status,
        )

    # ------------------------------------------------------------------
    # GET /settings/capacity
    # ------------------------------------------------------------------

    def get_capacity(self) -> CapacityOut:
        return CapacityOut(capacity=_get_capacity_value(self.db))

    # ------------------------------------------------------------------
    # PUT /settings/capacity
    # ------------------------------------------------------------------

    def set_capacity(self, data: CapacityIn) -> CapacityOut:
        """
        Actualiza (upsert) la capacidad en clinic_settings.
        La validación de que capacity > 0 ya la hace el schema CapacityIn.
        """
        row = self.db.query(ClinicSetting).filter(ClinicSetting.key == CAPACITY_KEY).first()
        if row is None:
            row = ClinicSetting(key=CAPACITY_KEY, value=str(data.capacity))
            self.db.add(row)
        else:
            row.value = str(data.capacity)
        self.db.commit()
        return CapacityOut(capacity=data.capacity)

    # ------------------------------------------------------------------
    # GET /waitlist
    # ------------------------------------------------------------------

    def list_waitlist(self, status: Optional[WaitlistStatus] = None) -> List[WaitlistEntryOut]:
        q = self.db.query(WaitlistEntry).order_by(WaitlistEntry.requested_at.asc(), WaitlistEntry.created_at.asc())
        if status is not None:
            q = q.filter(WaitlistEntry.status == status)
        entries = q.all()
        return [WaitlistEntryOut.model_validate(e) for e in entries]

    # ------------------------------------------------------------------
    # POST /waitlist
    # ------------------------------------------------------------------

    def create_waitlist_entry(
        self,
        data: WaitlistEntryCreate,
        created_by_user_id: Optional[int],
    ) -> WaitlistEntryOut:
        entry = WaitlistEntry(
            full_name=data.full_name,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            requested_at=data.requested_at or date_type.today(),
            referred_by=data.referred_by,
            notes=data.notes,
            status=WaitlistStatus.waiting,
            created_by_user_id=created_by_user_id,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return WaitlistEntryOut.model_validate(entry)

    # ------------------------------------------------------------------
    # PATCH /waitlist/{id}
    # ------------------------------------------------------------------

    def patch_waitlist_entry(self, entry_id: int, data: WaitlistEntryPatch) -> WaitlistEntryOut:
        entry = self.db.query(WaitlistEntry).filter(WaitlistEntry.id == entry_id).first()
        if entry is None:
            raise HTTPException(status_code=404, detail="Entrada de lista de espera no encontrada.")

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(entry, field, value)

        self.db.commit()
        self.db.refresh(entry)
        return WaitlistEntryOut.model_validate(entry)
