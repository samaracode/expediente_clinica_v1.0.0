"""
Capa de lógica de negocio para el módulo de Medicamentos (MAR).

Reglas de negocio críticas implementadas aquí:
- Generación lazy + idempotente de tomas al cargar el pase del día.
- Controlados: witness_user_id obligatorio al hacer record.
- Rechazado/Omitido: reason obligatorio.
- PRN: reason obligatorio.
- Auto-registro de administered_by_user_id y administered_at.
- Flag is_overdue: toma pending cuyo scheduled_at + MED_OMITTED_MARGIN_MIN ya pasó.
"""

from datetime import date, datetime, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.admission import Admission, AdmissionStatus
from app.models.medication import (
    AdministrationStatus,
    MedTimeSlot,
    Medication,
    MedicationAdministration,
    MedicationOrder,
    OrderStatus,
    ResidentAllergy,
    ScheduleType,
)
from app.models.resident import Resident
from app.schemas.medication import (
    AdministrationRecord,
    AllergyBrief,
    DailyPassOut,
    MedTimeSlotUpdate,
    MedicationAdministrationOut,
    MedicationCreate,
    MedicationOrderCreate,
    MedicationOrderPatch,
    MedicationOut,
    MedicationOrderOut,
    MedTimeSlotOut,
    PRNRecord,
    PassEntryOut,
    ResidentAllergyCreate,
    ResidentAllergyOut,
)

# Statuses que cuentan como "residente activo" para el pase.
ACTIVE_STATUSES = {
    AdmissionStatus.consents_pending,
    AdmissionStatus.assessment_in_progress,
    AdmissionStatus.treatment_active,
}


# ---------------------------------------------------------------------------
# Catálogo de medicamentos
# ---------------------------------------------------------------------------

class MedicationCatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[MedicationOut]:
        rows = self.db.query(Medication).order_by(Medication.name).all()
        return [MedicationOut.model_validate(r) for r in rows]

    def create(self, data: MedicationCreate) -> MedicationOut:
        med = Medication(**data.model_dump())
        self.db.add(med)
        self.db.commit()
        self.db.refresh(med)
        return MedicationOut.model_validate(med)


# ---------------------------------------------------------------------------
# Órdenes de medicamentos por admisión
# ---------------------------------------------------------------------------

class MedicationOrderService:
    def __init__(self, db: Session):
        self.db = db

    def _get_admission_or_404(self, admission_id: int) -> Admission:
        a = self.db.query(Admission).filter(Admission.id == admission_id).first()
        if not a:
            raise HTTPException(status_code=404, detail="Admisión no encontrada")
        return a

    def _get_order_or_404(self, order_id: int) -> MedicationOrder:
        o = self.db.query(MedicationOrder).filter(MedicationOrder.id == order_id).first()
        if not o:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        return o

    def list_by_admission(self, admission_id: int) -> List[MedicationOrderOut]:
        self._get_admission_or_404(admission_id)
        rows = (
            self.db.query(MedicationOrder)
            .filter(MedicationOrder.admission_id == admission_id)
            .order_by(MedicationOrder.created_at.desc())
            .all()
        )
        return [MedicationOrderOut.model_validate(r) for r in rows]

    def create(self, admission_id: int, data: MedicationOrderCreate) -> MedicationOrderOut:
        self._get_admission_or_404(admission_id)
        # Verificar que el medicamento exista
        if not self.db.query(Medication).filter(Medication.id == data.medication_id).first():
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")
        payload = data.model_dump()
        payload["admission_id"] = admission_id
        order = MedicationOrder(**payload)
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return MedicationOrderOut.model_validate(order)

    def list_administrations_by_order(self, order_id: int) -> List[MedicationAdministrationOut]:
        """Historial de tomas de una orden, ordenadas por scheduled_at desc (más reciente primero)."""
        order = self._get_order_or_404(order_id)
        rows = (
            self.db.query(MedicationAdministration)
            .filter(MedicationAdministration.order_id == order.id)
            .order_by(
                MedicationAdministration.scheduled_at.desc().nullsfirst(),
                MedicationAdministration.administered_at.desc().nullsfirst(),
            )
            .all()
        )
        now_utc = datetime.now(timezone.utc)
        margin = timedelta(minutes=settings.MED_OMITTED_MARGIN_MIN)
        result = []
        for adm in rows:
            scheduled = adm.scheduled_at
            if scheduled is not None and scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=timezone.utc)
            is_overdue = (
                adm.status == AdministrationStatus.pending
                and scheduled is not None
                and (scheduled + margin) < now_utc
            )
            out = MedicationAdministrationOut.model_validate(adm)
            out.is_overdue = is_overdue
            result.append(out)
        return result

    def patch(self, order_id: int, data: MedicationOrderPatch) -> MedicationOrderOut:
        order = self._get_order_or_404(order_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        self.db.commit()
        self.db.refresh(order)
        return MedicationOrderOut.model_validate(order)


# ---------------------------------------------------------------------------
# Pase del día (center-wide)
# ---------------------------------------------------------------------------

class DailyPassService:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_administrations_for_date(self, target_date: date) -> None:
        """
        Generación lazy + idempotente de tomas pending para la fecha dada.

        Para cada orden activa (scheduled) de una admisión activa cuyo rango
        start_date..end_date incluye target_date, crea una MedicationAdministration
        por cada slot_id en order.times, usando la hora del MedTimeSlot para
        calcular scheduled_at. No duplica si ya existe.
        """
        # Cargar todos los slots una sola vez
        slots = {str(s.id): s for s in self.db.query(MedTimeSlot).all()}

        # Admisiones activas con órdenes scheduled activas
        active_admissions = (
            self.db.query(Admission)
            .filter(Admission.status.in_(list(ACTIVE_STATUSES)))
            .all()
        )

        new_rows: List[MedicationAdministration] = []
        for admission in active_admissions:
            orders = (
                self.db.query(MedicationOrder)
                .filter(
                    MedicationOrder.admission_id == admission.id,
                    MedicationOrder.schedule_type == ScheduleType.scheduled,
                    MedicationOrder.status == OrderStatus.active,
                    MedicationOrder.start_date <= target_date,
                )
                .all()
            )
            for order in orders:
                # Verificar end_date
                if order.end_date and order.end_date < target_date:
                    continue

                times_list: List[str] = order.times or []
                for slot_key in times_list:
                    slot = slots.get(str(slot_key))
                    if slot is None:
                        continue
                    # Combinar fecha + hora del slot para scheduled_at (UTC naive → aware)
                    scheduled_naive = datetime.combine(target_date, slot.time)
                    scheduled_at = scheduled_naive.replace(tzinfo=timezone.utc)

                    # Idempotencia: buscar si ya existe
                    exists = (
                        self.db.query(MedicationAdministration)
                        .filter(
                            MedicationAdministration.order_id == order.id,
                            MedicationAdministration.scheduled_at == scheduled_at,
                        )
                        .first()
                    )
                    if exists:
                        continue

                    new_rows.append(
                        MedicationAdministration(
                            order_id=order.id,
                            admission_id=admission.id,
                            scheduled_at=scheduled_at,
                            status=AdministrationStatus.pending,
                        )
                    )

        if new_rows:
            self.db.add_all(new_rows)
            self.db.commit()

    def get_pass(self, target_date: date, slot_id: Optional[int] = None) -> DailyPassOut:
        """Genera (lazy) y devuelve el pase del día."""
        self._ensure_administrations_for_date(target_date)

        now_utc = datetime.now(timezone.utc)
        margin = timedelta(minutes=settings.MED_OMITTED_MARGIN_MIN)

        # Cargar todos los slots para el label
        slots_by_id = {s.id: s for s in self.db.query(MedTimeSlot).all()}

        # Obtener todas las tomas del día (scheduled_at en el rango del día dado)
        day_start = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        q = (
            self.db.query(MedicationAdministration)
            .join(MedicationOrder, MedicationAdministration.order_id == MedicationOrder.id)
            .join(Admission, MedicationAdministration.admission_id == Admission.id)
            .join(Resident, Admission.resident_id == Resident.id)
            .join(Medication, MedicationOrder.medication_id == Medication.id)
            .filter(
                MedicationAdministration.scheduled_at >= day_start,
                MedicationAdministration.scheduled_at < day_end,
                Admission.status.in_(list(ACTIVE_STATUSES)),
            )
        )

        if slot_id is not None:
            # Filtrar por slot: el scheduled_at debe corresponder a la hora de ese slot
            slot = slots_by_id.get(slot_id)
            if slot:
                slot_hour = slot.time.hour
                slot_minute = slot.time.minute
                # Filtrar por hora del slot en UTC
                from sqlalchemy import extract
                q = q.filter(
                    extract("hour", MedicationAdministration.scheduled_at) == slot_hour,
                    extract("minute", MedicationAdministration.scheduled_at) == slot_minute,
                )

        administrations = q.options(
            joinedload(MedicationAdministration.order).joinedload(MedicationOrder.medication),
            joinedload(MedicationAdministration.admission).joinedload(Admission.resident),
        ).order_by(MedicationAdministration.scheduled_at).all()

        # Pre-cargar alergias de los residentes involucrados (evita N+1)
        resident_ids = {
            adm.admission.resident.id
            for adm in administrations
            if adm.admission and adm.admission.resident
        }
        allergies_by_resident: dict[int, List[ResidentAllergy]] = {}
        if resident_ids:
            allergy_rows = (
                self.db.query(ResidentAllergy)
                .filter(ResidentAllergy.resident_id.in_(list(resident_ids)))
                .all()
            )
            for a in allergy_rows:
                allergies_by_resident.setdefault(a.resident_id, []).append(a)

        entries: List[PassEntryOut] = []
        for adm in administrations:
            order = adm.order
            medication = order.medication
            admission = adm.admission
            resident = admission.resident

            # Determinar label del slot
            slot_label: Optional[str] = None
            if adm.scheduled_at:
                # Buscar slot que coincida con la hora
                for s in slots_by_id.values():
                    if (s.time.hour == adm.scheduled_at.hour and
                            s.time.minute == adm.scheduled_at.minute):
                        slot_label = s.label
                        break

            # Flag overdue: pending cuyo scheduled_at + margen ya pasó
            is_overdue = False
            if adm.status == AdministrationStatus.pending and adm.scheduled_at:
                # Normalizar a aware (SQLite devuelve naive; PostgreSQL devuelve aware)
                scheduled = adm.scheduled_at
                if scheduled.tzinfo is None:
                    scheduled = scheduled.replace(tzinfo=timezone.utc)
                if (scheduled + margin) < now_utc:
                    is_overdue = True
                    # TODO: push notification — integrar con NotificationService si se agrega
                    # un endpoint/método de notificación de dosis vencidas.

            resident_allergies = [
                AllergyBrief(id=a.id, substance=a.substance, severity=a.severity)
                for a in allergies_by_resident.get(resident.id, [])
            ]

            entries.append(
                PassEntryOut(
                    administration_id=adm.id,
                    order_id=order.id,
                    admission_id=admission.id,
                    resident_id=resident.id,
                    resident_name=f"{resident.first_name} {resident.last_name}",
                    medication_name=medication.name,
                    dose=order.dose,
                    route=order.route,
                    is_controlled=order.is_controlled,
                    scheduled_at=adm.scheduled_at,
                    slot_label=slot_label,
                    status=adm.status,
                    administered_at=adm.administered_at,
                    administered_by_user_id=adm.administered_by_user_id,
                    witness_user_id=adm.witness_user_id,
                    reason=adm.reason,
                    notes=adm.notes,
                    is_overdue=is_overdue,
                    allergies=resident_allergies,
                )
            )

        return DailyPassOut(date=target_date, entries=entries)


# ---------------------------------------------------------------------------
# Registro de tomas (administraciones)
# ---------------------------------------------------------------------------

class AdministrationService:
    def __init__(self, db: Session):
        self.db = db

    def _get_administration_or_404(self, adm_id: int) -> MedicationAdministration:
        row = (
            self.db.query(MedicationAdministration)
            .options(joinedload(MedicationAdministration.order))
            .filter(MedicationAdministration.id == adm_id)
            .first()
        )
        if not row:
            raise HTTPException(status_code=404, detail="Administración no encontrada")
        return row

    def record(
        self,
        adm_id: int,
        data: AdministrationRecord,
        current_user_id: int,
    ) -> MedicationAdministrationOut:
        adm = self._get_administration_or_404(adm_id)
        order = adm.order

        # Regla: controlado → witness obligatorio
        if order.is_controlled and not data.witness_user_id:
            raise HTTPException(
                status_code=400,
                detail="Las tomas de medicamentos controlados requieren un testigo (witness_user_id).",
            )

        # Regla: rechazado/omitido → reason obligatorio
        if data.status in (AdministrationStatus.refused, AdministrationStatus.omitted):
            if not data.reason:
                raise HTTPException(
                    status_code=400,
                    detail="Se debe indicar el motivo (reason) cuando una toma es rechazada u omitida.",
                )

        adm.status = data.status
        adm.administered_at = data.administered_at or datetime.now(timezone.utc)
        adm.administered_by_user_id = current_user_id
        adm.witness_user_id = data.witness_user_id
        adm.reason = data.reason
        adm.notes = data.notes

        self.db.commit()
        self.db.refresh(adm)

        now_utc = datetime.now(timezone.utc)
        margin = timedelta(minutes=settings.MED_OMITTED_MARGIN_MIN)
        scheduled = adm.scheduled_at
        if scheduled is not None and scheduled.tzinfo is None:
            scheduled = scheduled.replace(tzinfo=timezone.utc)
        is_overdue = (
            adm.status == AdministrationStatus.pending
            and scheduled is not None
            and (scheduled + margin) < now_utc
        )
        out = MedicationAdministrationOut.model_validate(adm)
        out.is_overdue = is_overdue
        return out

    def record_prn(
        self,
        admission_id: int,
        order_id: int,
        data: PRNRecord,
        current_user_id: int,
    ) -> MedicationAdministrationOut:
        # Verificar que la orden exista y pertenezca a la admisión
        order = (
            self.db.query(MedicationOrder)
            .filter(
                MedicationOrder.id == order_id,
                MedicationOrder.admission_id == admission_id,
            )
            .first()
        )
        if not order:
            raise HTTPException(status_code=404, detail="Orden no encontrada para esta admisión")

        # Regla PRN: reason siempre obligatorio (ya viene requerido en el schema,
        # pero lo validamos explícitamente para devolver 400 en lugar de 422)
        if not data.reason:
            raise HTTPException(
                status_code=400,
                detail="Se debe indicar el motivo (reason) de la toma PRN.",
            )

        now_utc = datetime.now(timezone.utc)
        adm = MedicationAdministration(
            order_id=order_id,
            admission_id=admission_id,
            scheduled_at=None,  # PRN: sin hora pautada
            status=AdministrationStatus.taken,
            administered_at=data.administered_at or now_utc,
            administered_by_user_id=current_user_id,
            witness_user_id=data.witness_user_id,
            reason=data.reason,
            notes=data.notes,
        )
        self.db.add(adm)
        self.db.commit()
        self.db.refresh(adm)

        out = MedicationAdministrationOut.model_validate(adm)
        out.is_overdue = False
        return out


# ---------------------------------------------------------------------------
# Alergias de residente
# ---------------------------------------------------------------------------

class ResidentAllergyService:
    def __init__(self, db: Session):
        self.db = db

    def _get_resident_or_404(self, resident_id: int) -> Resident:
        r = self.db.query(Resident).filter(Resident.id == resident_id).first()
        if not r:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return r

    def list(self, resident_id: int) -> List[ResidentAllergyOut]:
        self._get_resident_or_404(resident_id)
        rows = (
            self.db.query(ResidentAllergy)
            .filter(ResidentAllergy.resident_id == resident_id)
            .all()
        )
        return [ResidentAllergyOut.model_validate(r) for r in rows]

    def create(self, resident_id: int, data: ResidentAllergyCreate) -> ResidentAllergyOut:
        self._get_resident_or_404(resident_id)
        allergy = ResidentAllergy(
            resident_id=resident_id,
            substance=data.substance,
            reaction=data.reaction,
            severity=data.severity,
        )
        self.db.add(allergy)
        self.db.commit()
        self.db.refresh(allergy)
        return ResidentAllergyOut.model_validate(allergy)

    def delete(self, resident_id: int, allergy_id: int) -> None:
        allergy = (
            self.db.query(ResidentAllergy)
            .filter(
                ResidentAllergy.id == allergy_id,
                ResidentAllergy.resident_id == resident_id,
            )
            .first()
        )
        if not allergy:
            raise HTTPException(status_code=404, detail="Alergia no encontrada")
        self.db.delete(allergy)
        self.db.commit()


# ---------------------------------------------------------------------------
# Franjas horarias (settings)
# ---------------------------------------------------------------------------

class MedTimeSlotsService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> List[MedTimeSlotOut]:
        rows = self.db.query(MedTimeSlot).order_by(MedTimeSlot.sort_order, MedTimeSlot.time).all()
        return [MedTimeSlotOut.model_validate(r) for r in rows]

    def put(self, slots_data: List[MedTimeSlotUpdate]) -> List[MedTimeSlotOut]:
        """
        Reemplaza la lista completa de franjas horarias.
        Si un item trae id existente → actualiza.
        Si no trae id → crea.
        Franjas no mencionadas se eliminan.
        """
        incoming_ids = {item.id for item in slots_data if item.id is not None}

        # Eliminar los que no están en la nueva lista
        existing = self.db.query(MedTimeSlot).all()
        for slot in existing:
            if slot.id not in incoming_ids:
                self.db.delete(slot)

        result = []
        for item in slots_data:
            if item.id is not None:
                slot = self.db.query(MedTimeSlot).filter(MedTimeSlot.id == item.id).first()
                if slot:
                    slot.label = item.label
                    slot.time = item.time
                    slot.sort_order = item.sort_order
                    result.append(slot)
                    continue
            # Crear nuevo
            slot = MedTimeSlot(label=item.label, time=item.time, sort_order=item.sort_order)
            self.db.add(slot)
            result.append(slot)

        self.db.commit()
        for slot in result:
            self.db.refresh(slot)

        return [MedTimeSlotOut.model_validate(s) for s in result]
