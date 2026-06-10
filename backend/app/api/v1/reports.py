from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission, AdmissionStatus, AdmissionType
from app.models.follow_up import Consultation
from app.models.resident import Resident
from app.models.treatment import StageStatus, TreatmentPlan
from app.models.user import Professional, TreatmentArea, User
from app.schemas.reports import AdmissionReportRow, ConsultationReportRow, TreatmentProgressRow

router = APIRouter()


def _str_enum(val) -> str:
    return val.value if hasattr(val, "value") else str(val)


@router.get("/admissions", response_model=List[AdmissionReportRow])
def report_admissions(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows = (
        db.query(Admission, Resident)
        .join(Resident, Admission.resident_id == Resident.id)
        .order_by(Admission.admission_date.desc())
        .limit(500)
        .all()
    )
    return [
        AdmissionReportRow(
            id=a.id,
            admission_number=a.admission_number,
            resident_name=f"{r.first_name} {r.last_name}",
            admission_date=str(a.admission_date),
            discharge_date=str(a.discharge_date) if a.discharge_date else None,
            status=_str_enum(a.status),
            admission_type=_str_enum(a.admission_type),
        )
        for a, r in rows
    ]


@router.get("/consultations", response_model=List[ConsultationReportRow])
def report_consultations(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows = (
        db.query(Consultation, Admission, Resident)
        .join(Admission, Consultation.admission_id == Admission.id)
        .join(Resident, Admission.resident_id == Resident.id)
        .options(
            joinedload(Consultation.professional),
            joinedload(Consultation.area),
        )
        .order_by(Consultation.consultation_date.desc())
        .limit(500)
        .all()
    )
    result = []
    for c, a, r in rows:
        prof_name = "—"
        if c.professional:
            prof_name = f"{c.professional.first_name} {c.professional.last_name}"
        result.append(
            ConsultationReportRow(
                id=c.id,
                consultation_date=str(c.consultation_date),
                professional_name=prof_name,
                area_name=c.area.name if c.area else None,
                consultation_type=c.consultation_type,
                resident_name=f"{r.first_name} {r.last_name}",
            )
        )
    return result


@router.get("/treatment-progress", response_model=List[TreatmentProgressRow])
def report_treatment_progress(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    active_statuses = [AdmissionStatus.treatment_active, AdmissionStatus.assessment_in_progress]
    admissions = (
        db.query(Admission, Resident)
        .join(Resident, Admission.resident_id == Resident.id)
        .filter(Admission.status.in_(active_statuses))
        .order_by(Admission.admission_date.desc())
        .limit(200)
        .all()
    )

    result = []
    for admission, resident in admissions:
        plan = (
            db.query(TreatmentPlan)
            .options(joinedload(TreatmentPlan.stages))
            .filter(TreatmentPlan.admission_id == admission.id)
            .first()
        )
        stages_completed = 0
        current_stage = None
        if plan:
            for stage in plan.stages:
                st = _str_enum(stage.status)
                if st == "completed":
                    stages_completed += 1
                if st == "active" and current_stage is None:
                    sn = _str_enum(stage.stage_name)
                    current_stage = sn

        result.append(
            TreatmentProgressRow(
                admission_id=admission.id,
                admission_number=admission.admission_number,
                resident_name=f"{resident.first_name} {resident.last_name}",
                status=_str_enum(admission.status),
                stages_completed=stages_completed,
                current_stage=current_stage,
            )
        )
    return result
