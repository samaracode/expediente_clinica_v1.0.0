from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.admission import Admission
from app.models.follow_up import Consultation, ExitPass, PassStatus
from app.models.resident import Resident
from app.models.treatment import TreatmentPlan, TreatmentStage, StageStatus

router = APIRouter()


class Notification(BaseModel):
    type: str
    message: str
    entity_id: int
    entity_type: str
    due_date: Optional[str] = None


@router.get("/notifications", response_model=list[Notification])
def get_notifications(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    today = date.today()
    results: list[Notification] = []

    # 1. Próximas citas (next 3 days)
    upcoming_cutoff = today + timedelta(days=3)
    upcoming = (
        db.query(Consultation)
        .options(
            joinedload(Consultation.admission).joinedload(Admission.resident)
        )
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
        when = "hoy" if days_away == 0 else (f"mañana" if days_away == 1 else f"en {days_away} días")
        results.append(
            Notification(
                type="upcoming_appointment",
                message=f"Cita {when}: {resident.first_name} {resident.last_name}",
                entity_id=c.admission_id,
                entity_type="consultation",
                due_date=str(c.next_appointment_date),
            )
        )

    # 2. Permisos de salida vencidos (expected return < today, not returned)
    overdue = (
        db.query(ExitPass)
        .options(
            joinedload(ExitPass.admission).joinedload(Admission.resident)
        )
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

    # 3. Etapas de tratamiento por vencer (next 7 days)
    stage_cutoff = today + timedelta(days=7)
    stages = (
        db.query(TreatmentStage)
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
        when = "hoy" if days_left == 0 else (f"mañana" if days_left == 1 else f"en {days_left} días")
        results.append(
            Notification(
                type="upcoming_stage_end",
                message=f"Etapa '{stage.stage_name.value}' vence {when}: {resident.first_name} {resident.last_name}",
                entity_id=admission.id,
                entity_type="treatment_stage",
                due_date=str(stage.end_date),
            )
        )

    # Sort by due_date ascending
    results.sort(key=lambda n: n.due_date or "9999-99-99")
    return results
