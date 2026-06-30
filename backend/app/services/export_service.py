from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission
from app.models.assessment import (
    OccupationalTherapyAssessment,
    PsychologyAssessment,
    SocialWorkAssessment,
    TherapeuticAssessment,
)
from app.models.consent import ConsentRecord
from app.models.follow_up import Consultation, DailyLog
from app.models.medical import MedicalRecord
from app.models.resident import PatientRelative, Resident
from app.models.treatment import TreatmentPlan

CONSENT_LABELS: dict[str, str] = {
    "INTERNMENT_SERVICE": "Servicio de internamiento",
    "INTERNMENT": "Internamiento",
    "SEARCH": "Requisa",
    "DRUG_TEST": "Prueba de droga",
    "CCTV": "Videovigilancia",
    "INFO_RELEASE": "Liberación de información",
    "WEAPONS": "Armas",
    "IAFA_ACTIONS": "Acciones IAFA",
    "INDIVIDUAL_APPROACH": "Abordaje individual",
    "REFERRAL": "Referencia",
    "RECORD_ACCESS": "Acceso al expediente",
    "RIGHTS_FOCUS": "Enfoque de derechos",
    "LABOR": "Laboral",
    "NON_DISCRIMINATION": "No discriminación",
    "SPONSOR": "Patrocinador",
    "MANUAL": "Manual de convivencia",
    "LABOR_PROVISION": "Provisión laboral",
}

STATUS_LABELS: dict[str, str] = {
    "intake_pending": "Pendiente de ingreso",
    "consents_pending": "Consentimientos pendientes",
    "assessment_in_progress": "Evaluación en progreso",
    "treatment_active": "Tratamiento activo",
    "discharged": "Egresado",
    "abandoned": "Abandono",
}

SEX_LABELS = {"male": "Masculino", "female": "Femenino", "other": "Otro"}

MARITAL_LABELS = {
    "single": "Soltero/a",
    "married": "Casado/a",
    "divorced": "Divorciado/a",
    "widowed": "Viudo/a",
    "common_law": "Unión libre",
}


class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def get_admission_export_context(self, admission_id: int) -> dict:
        admission = (
            self.db.query(Admission)
            .filter(Admission.id == admission_id, Admission.is_deleted == False)  # noqa: E712
            .first()
        )
        if not admission:
            raise HTTPException(status_code=404, detail="Admisión no encontrada")

        resident: Resident = self.db.query(Resident).filter(Resident.id == admission.resident_id).first()

        relatives_raw = (
            self.db.query(PatientRelative)
            .options(joinedload(PatientRelative.relative))
            .filter(PatientRelative.resident_id == resident.id)
            .all()
        )

        consents_raw = self.db.query(ConsentRecord).filter(ConsentRecord.admission_id == admission_id).all()
        consents = [
            {
                "label": CONSENT_LABELS.get(c.consent_type.value, c.consent_type.value),
                "is_signed": c.is_signed,
                "signed_at": str(c.signed_at.date()) if c.signed_at else None,
            }
            for c in consents_raw
        ]

        medical = self.db.query(MedicalRecord).filter(MedicalRecord.admission_id == admission_id).first()
        therapeutic = (
            self.db.query(TherapeuticAssessment)
            .filter(TherapeuticAssessment.admission_id == admission_id)
            .first()
        )
        social_work = (
            self.db.query(SocialWorkAssessment)
            .filter(SocialWorkAssessment.admission_id == admission_id)
            .first()
        )
        psychology = (
            self.db.query(PsychologyAssessment)
            .filter(PsychologyAssessment.admission_id == admission_id)
            .first()
        )
        occupational = (
            self.db.query(OccupationalTherapyAssessment)
            .filter(OccupationalTherapyAssessment.admission_id == admission_id)
            .first()
        )
        treatment_plan = (
            self.db.query(TreatmentPlan)
            .filter(TreatmentPlan.admission_id == admission_id)
            .first()
        )
        daily_logs = (
            self.db.query(DailyLog)
            .filter(DailyLog.admission_id == admission_id, DailyLog.is_deleted == False)  # noqa: E712
            .order_by(DailyLog.log_date.desc())
            .limit(30)
            .all()
        )
        consultations = (
            self.db.query(Consultation)
            .options(joinedload(Consultation.professional), joinedload(Consultation.area))
            .filter(Consultation.admission_id == admission_id, Consultation.is_deleted == False)  # noqa: E712
            .order_by(Consultation.consultation_date.desc())
            .all()
        )

        return {
            "admission": admission,
            "resident": resident,
            "relatives": [pr.relative for pr in relatives_raw],
            "consents": consents,
            "economic": admission.economic_situation,
            "medical": medical,
            "therapeutic": therapeutic,
            "social_work": social_work,
            "psychology": psychology,
            "occupational": occupational,
            "treatment_plan": treatment_plan,
            "daily_logs": daily_logs,
            "consultations": consultations,
            "status_label": STATUS_LABELS.get(admission.status.value, admission.status.value),
            "sex_label": SEX_LABELS.get(resident.sex.value if resident.sex else "", "—"),
            "marital_label": MARITAL_LABELS.get(
                resident.marital_status.value if resident.marital_status else "", "—"
            ),
        }
