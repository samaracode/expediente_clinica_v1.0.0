from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, ModuleRequired
from app.db.session import get_db
from app.models.admission import Admission
from app.models.assessment import TherapeuticAssessment
from app.models.user import Module, User
from app.schemas.therapeutic import TherapeuticAssessmentOut, TherapeuticAssessmentUpsert

router = APIRouter()
_role = ModuleRequired(Module.therapeutic)


def _build_out(record: TherapeuticAssessment) -> TherapeuticAssessmentOut:
    return TherapeuticAssessmentOut(
        id=record.id,
        admission_id=record.admission_id,
        assessor_id=record.assessor_id,
        assessment_date=str(record.assessment_date) if record.assessment_date else None,
        initial_summary=record.initial_summary,
        clinical_history_summary=record.clinical_history_summary,
        europal_si_notes=(record.europal_si_data or {}).get("notes"),
        socrates_notes=(record.socrates_data or {}).get("notes"),
        urica_notes=(record.urica_data or {}).get("notes"),
        afc_analysis_notes=(record.afc_analysis or {}).get("notes"),
        relapse_prevention_interview=record.relapse_prevention_interview,
        relapse_prevention_plan=record.relapse_prevention_plan,
        completion_status=record.completion_status or "pending",
    )


@router.get("/{admission_id}/therapeutic", response_model=TherapeuticAssessmentOut)
def get_therapeutic(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(TherapeuticAssessment)
        .filter(TherapeuticAssessment.admission_id == admission_id)
        .first()
    )
    if not record:
        return TherapeuticAssessmentOut(admission_id=admission_id)
    return _build_out(record)


@router.put("/{admission_id}/therapeutic", response_model=TherapeuticAssessmentOut)
def upsert_therapeutic(
    admission_id: int,
    data: TherapeuticAssessmentUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(TherapeuticAssessment)
        .filter(TherapeuticAssessment.admission_id == admission_id)
        .first()
    )

    assessment_date = date.fromisoformat(data.assessment_date) if data.assessment_date else None
    europal_si_data = {"notes": data.europal_si_notes} if data.europal_si_notes else None
    socrates_data = {"notes": data.socrates_notes} if data.socrates_notes else None
    urica_data = {"notes": data.urica_notes} if data.urica_notes else None
    afc_analysis = {"notes": data.afc_analysis_notes} if data.afc_analysis_notes else None

    if record:
        record.assessment_date = assessment_date
        record.initial_summary = data.initial_summary
        record.clinical_history_summary = data.clinical_history_summary
        record.europal_si_data = europal_si_data
        record.socrates_data = socrates_data
        record.urica_data = urica_data
        record.afc_analysis = afc_analysis
        record.relapse_prevention_interview = data.relapse_prevention_interview
        record.relapse_prevention_plan = data.relapse_prevention_plan
        record.completion_status = data.completion_status
    else:
        record = TherapeuticAssessment(
            admission_id=admission_id,
            assessment_date=assessment_date,
            initial_summary=data.initial_summary,
            clinical_history_summary=data.clinical_history_summary,
            europal_si_data=europal_si_data,
            socrates_data=socrates_data,
            urica_data=urica_data,
            afc_analysis=afc_analysis,
            relapse_prevention_interview=data.relapse_prevention_interview,
            relapse_prevention_plan=data.relapse_prevention_plan,
            completion_status=data.completion_status,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return _build_out(record)
