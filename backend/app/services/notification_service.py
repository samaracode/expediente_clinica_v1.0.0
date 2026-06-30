from datetime import date, datetime, timedelta, timezone
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.admission import Admission, AdmissionStatus
from app.models.follow_up import Consultation, ExitPass, PassStatus
from app.models.medication import (
    AdministrationStatus,
    MedicationAdministration,
    MedicationOrder,
    Medication,
)
from app.models.resident import Resident
from app.models.treatment import TreatmentPlan, TreatmentStage, StageStatus
from app.models.attendance import AttendanceEntry, AttendanceRollCall, PresenceStatus


class Notification(BaseModel):
    type: str
    message: str
    entity_id: int
    entity_type: str
    due_date: Optional[str] = None


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_notifications(self) -> list[Notification]:
        today = date.today()
        results: list[Notification] = []

        upcoming_cutoff = today + timedelta(days=3)
        upcoming = (
            self.db.query(Consultation)
            .options(joinedload(Consultation.admission).joinedload(Admission.resident))
            .filter(
                Consultation.is_deleted == False,  # noqa: E712
                Consultation.next_appointment_date >= today,
                Consultation.next_appointment_date <= upcoming_cutoff,
            )
            .order_by(Consultation.next_appointment_date.asc())
            .all()
        )
        for c in upcoming:
            resident: Resident = c.admission.resident
            days_away = (c.next_appointment_date - today).days
            when = "hoy" if days_away == 0 else ("mañana" if days_away == 1 else f"en {days_away} días")
            results.append(
                Notification(
                    type="upcoming_appointment",
                    message=f"Cita {when}: {resident.first_name} {resident.last_name}",
                    entity_id=c.admission_id,
                    entity_type="consultation",
                    due_date=str(c.next_appointment_date),
                )
            )

        overdue = (
            self.db.query(ExitPass)
            .options(joinedload(ExitPass.admission).joinedload(Admission.resident))
            .filter(
                ExitPass.status == PassStatus.approved,
                ExitPass.return_date_expected != None,  # noqa: E711
                ExitPass.return_date_actual == None,  # noqa: E711
            )
            .all()
        )
        for ep in overdue:
            if ep.return_date_expected and ep.return_date_expected.date() < today:
                resident = ep.admission.resident
                days_late = (today - ep.return_date_expected.date()).days
                results.append(
                    Notification(
                        type="overdue_exit_pass",
                        message=f"Permiso vencido hace {days_late} día{'s' if days_late != 1 else ''}: {resident.first_name} {resident.last_name}",
                        entity_id=ep.admission_id,
                        entity_type="exit_pass",
                        due_date=str(ep.return_date_expected.date()),
                    )
                )

        stage_cutoff = today + timedelta(days=7)
        stages = (
            self.db.query(TreatmentStage)
            .options(
                joinedload(TreatmentStage.treatment_plan)
                .joinedload(TreatmentPlan.admission)
                .joinedload(Admission.resident)
            )
            .filter(
                TreatmentStage.status == StageStatus.active,
                TreatmentStage.end_date != None,  # noqa: E711
                TreatmentStage.end_date >= today,
                TreatmentStage.end_date <= stage_cutoff,
            )
            .order_by(TreatmentStage.end_date.asc())
            .all()
        )
        for stage in stages:
            admission = stage.treatment_plan.admission
            resident = admission.resident
            days_left = (stage.end_date - today).days
            when = "hoy" if days_left == 0 else ("mañana" if days_left == 1 else f"en {days_left} días")
            results.append(
                Notification(
                    type="upcoming_stage_end",
                    message=f"Etapa '{stage.stage_name.value}' vence {when}: {resident.first_name} {resident.last_name}",
                    entity_id=admission.id,
                    entity_type="treatment_stage",
                    due_date=str(stage.end_date),
                )
            )

        # Dosis omitidas: tomas pending cuyo scheduled_at + margen ya pasó
        now_utc = datetime.now(timezone.utc)
        margin = timedelta(minutes=settings.MED_OMITTED_MARGIN_MIN)
        pending_adms = (
            self.db.query(MedicationAdministration)
            .join(MedicationOrder, MedicationAdministration.order_id == MedicationOrder.id)
            .join(Medication, MedicationOrder.medication_id == Medication.id)
            .join(Admission, MedicationAdministration.admission_id == Admission.id)
            .join(Resident, Admission.resident_id == Resident.id)
            .options(
                joinedload(MedicationAdministration.order).joinedload(MedicationOrder.medication),
                joinedload(MedicationAdministration.admission).joinedload(Admission.resident),
            )
            .filter(
                MedicationAdministration.status == AdministrationStatus.pending,
                MedicationAdministration.scheduled_at != None,  # noqa: E711
                # Solo admisiones activas: evita ruido por residentes egresados/abandonados
                # con tomas viejas que quedaron pending.
                Admission.status.in_(
                    [
                        AdmissionStatus.consents_pending,
                        AdmissionStatus.assessment_in_progress,
                        AdmissionStatus.treatment_active,
                    ]
                ),
            )
            .order_by(MedicationAdministration.scheduled_at.asc())
            .all()
        )
        for adm in pending_adms:
            # Normalizar a aware para comparar correctamente (SQLite devuelve naive)
            scheduled = adm.scheduled_at
            if scheduled.tzinfo is None:
                scheduled = scheduled.replace(tzinfo=timezone.utc)
            if (scheduled + margin) < now_utc:
                medication_name = adm.order.medication.name
                resident = adm.admission.resident
                results.append(
                    Notification(
                        type="overdue_medication",
                        message=f"Dosis vencida: {medication_name} de {resident.first_name} {resident.last_name}",
                        entity_id=adm.admission_id,
                        entity_type="medication_administration",
                        due_date=str(scheduled.date()),
                    )
                )

        # Ausentes sin permiso: entries del último roll-call del día de HOY con actual_status = absent_without_leave
        today = date.today()
        latest_roll_call = (
            self.db.query(AttendanceRollCall)
            .filter(AttendanceRollCall.date == today)
            .order_by(AttendanceRollCall.conducted_at.desc())
            .first()
        )
        if latest_roll_call:
            awol_entries = (
                self.db.query(AttendanceEntry)
                .join(Admission, AttendanceEntry.admission_id == Admission.id)
                .join(Resident, Admission.resident_id == Resident.id)
                .options(
                    joinedload(AttendanceEntry.admission).joinedload(Admission.resident)
                )
                .filter(
                    AttendanceEntry.roll_call_id == latest_roll_call.id,
                    AttendanceEntry.actual_status == PresenceStatus.absent_without_leave,
                )
                .all()
            )
            for entry in awol_entries:
                resident = entry.admission.resident
                results.append(
                    Notification(
                        type="absent_without_leave",
                        message=f"Ausente sin permiso: {resident.first_name} {resident.last_name}",
                        entity_id=entry.admission_id,
                        entity_type="attendance",
                    )
                )

        results.sort(key=lambda n: n.due_date or "9999-99-99")
        return results
