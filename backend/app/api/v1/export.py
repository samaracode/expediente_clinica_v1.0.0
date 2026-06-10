import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pdfkit
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.admission import Admission
from app.models.assessment import (
    OccupationalTherapyAssessment,
    PsychologyAssessment,
    SocialWorkAssessment,
    TherapeuticAssessment,
)
from app.models.consent import ConsentRecord, PersonalItemsInventory
from app.models.follow_up import Consultation, DailyLog
from app.models.medical import MedicalRecord
from app.models.resident import PatientRelative, Relative, Resident
from app.models.treatment import TreatmentPlan

router = APIRouter()

_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "app" / "templates"
_CONSENT_LABELS: dict[str, str] = {
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
_STATUS_LABELS: dict[str, str] = {
    "intake_pending": "Pendiente de ingreso",
    "consents_pending": "Consentimientos pendientes",
    "assessment_in_progress": "Evaluación en progreso",
    "treatment_active": "Tratamiento activo",
    "discharged": "Egresado",
    "abandoned": "Abandono",
}
_SEX_LABELS = {"male": "Masculino", "female": "Femenino", "other": "Otro"}
_MARITAL_LABELS = {
    "single": "Soltero/a",
    "married": "Casado/a",
    "divorced": "Divorciado/a",
    "widowed": "Viudo/a",
    "common_law": "Unión libre",
}


def _jinja_env() -> Environment:
    # __file__ = app/api/v1/export.py → .parent×3 = app/ → templates/
    templates_path = Path(__file__).parent.parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(templates_path)), autoescape=True)


@router.get("/{admission_id}/export/pdf")
def export_admission_pdf(
    admission_id: int,
    bg: BackgroundTasks,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    admission = (
        db.query(Admission)
        .filter(Admission.id == admission_id, Admission.is_deleted == False)  # noqa: E712
        .first()
    )
    if not admission:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    resident: Resident = db.query(Resident).filter(Resident.id == admission.resident_id).first()

    # Relatives — build flat dicts so the template doesn't need to traverse bridge
    relatives_raw = (
        db.query(PatientRelative)
        .options(joinedload(PatientRelative.relative))
        .filter(PatientRelative.resident_id == resident.id)
        .all()
    )
    relatives = [
        {
            "first_name": pr.relative.first_name,
            "last_name": pr.relative.last_name,
            "relation_type": pr.relation_type,
            "id_number": pr.relative.id_number,
            "phone": pr.relative.phone,
        }
        for pr in relatives_raw
    ]

    # Consents
    consents_raw = db.query(ConsentRecord).filter(ConsentRecord.admission_id == admission_id).all()
    consents = [
        {
            "label": _CONSENT_LABELS.get(c.consent_type.value, c.consent_type.value),
            "is_signed": c.is_signed,
            "signed_at": str(c.signed_at.date()) if c.signed_at else None,
        }
        for c in consents_raw
    ]

    # Economic situation
    economic = admission.economic_situation

    # Medical
    medical = db.query(MedicalRecord).filter(MedicalRecord.admission_id == admission_id).first()

    # Assessments
    therapeutic = (
        db.query(TherapeuticAssessment)
        .filter(TherapeuticAssessment.admission_id == admission_id)
        .first()
    )
    social_work = (
        db.query(SocialWorkAssessment)
        .filter(SocialWorkAssessment.admission_id == admission_id)
        .first()
    )
    psychology = (
        db.query(PsychologyAssessment)
        .filter(PsychologyAssessment.admission_id == admission_id)
        .first()
    )
    occupational = (
        db.query(OccupationalTherapyAssessment)
        .filter(OccupationalTherapyAssessment.admission_id == admission_id)
        .first()
    )

    # Treatment plan
    treatment_plan = (
        db.query(TreatmentPlan)
        .filter(TreatmentPlan.admission_id == admission_id)
        .first()
    )

    # Daily logs (last 30, most recent first for display)
    daily_logs = (
        db.query(DailyLog)
        .filter(DailyLog.admission_id == admission_id, DailyLog.is_deleted == False)  # noqa: E712
        .order_by(DailyLog.log_date.desc())
        .limit(30)
        .all()
    )

    # Consultations
    consultations = (
        db.query(Consultation)
        .options(joinedload(Consultation.professional), joinedload(Consultation.area))
        .filter(Consultation.admission_id == admission_id, Consultation.is_deleted == False)  # noqa: E712
        .order_by(Consultation.consultation_date.desc())
        .all()
    )

    generated_at = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    env = _jinja_env()
    template = env.get_template("admission_report.html")
    html = template.render(
        admission=admission,
        resident=resident,
        relatives=[pr.relative for pr in relatives],
        consents=consents,
        economic=economic,
        medical=medical,
        therapeutic=therapeutic,
        social_work=social_work,
        psychology=psychology,
        occupational=occupational,
        treatment_plan=treatment_plan,
        daily_logs=daily_logs,
        consultations=consultations,
        status_label=_STATUS_LABELS.get(admission.status.value, admission.status.value),
        sex_label=_SEX_LABELS.get(resident.sex.value if resident.sex else "", "—"),
        marital_label=_MARITAL_LABELS.get(
            resident.marital_status.value if resident.marital_status else "", "—"
        ),
        generated_at=generated_at,
    )

    options = {
        "page-size": "A4",
        "margin-top": "0mm",
        "margin-right": "0mm",
        "margin-bottom": "0mm",
        "margin-left": "0mm",
        "encoding": "UTF-8",
        "no-outline": None,
        "enable-local-file-access": None,
    }

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        pdfkit.from_string(html, tmp_path, options=options)
    except Exception as exc:
        os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {exc}") from exc

    bg.add_task(os.unlink, tmp_path)
    filename = f"expediente_{admission.admission_number}.pdf"
    return FileResponse(path=tmp_path, media_type="application/pdf", filename=filename)
