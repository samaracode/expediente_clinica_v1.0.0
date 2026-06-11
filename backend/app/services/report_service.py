from typing import List

from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission, AdmissionStatus
from app.models.follow_up import Consultation
from app.models.resident import Resident
from app.models.treatment import StageStatus, TreatmentPlan
from app.schemas.reports import AdmissionReportRow, ConsultationReportRow, TreatmentProgressRow


def _str_enum(val) -> str:
    return val.value if hasattr(val, "value") else str(val)


class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def admissions_report(self) -> List[AdmissionReportRow]:
        rows = (
            self.db.query(Admission, Resident)
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

    def consultations_report(self) -> List[ConsultationReportRow]:
        rows = (
            self.db.query(Consultation, Admission, Resident)
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

    def treatment_progress_report(self) -> List[TreatmentProgressRow]:
        active_statuses = [AdmissionStatus.treatment_active, AdmissionStatus.assessment_in_progress]
        admissions = (
            self.db.query(Admission, Resident)
            .join(Resident, Admission.resident_id == Resident.id)
            .filter(Admission.status.in_(active_statuses))
            .order_by(Admission.admission_date.desc())
            .limit(200)
            .all()
        )
        result = []
        for admission, resident in admissions:
            plan = (
                self.db.query(TreatmentPlan)
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
                        current_stage = _str_enum(stage.stage_name)
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
