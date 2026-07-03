from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, ModuleRequired
from app.db.session import get_db
from app.models.admission import Admission
from app.models.assessment import SocialWorkAssessment
from app.models.user import Module, User
from app.schemas.social_work import SocialWorkAssessmentOut, SocialWorkAssessmentUpsert

router = APIRouter()
_role = ModuleRequired(Module.social_work)


def _build_out(record: SocialWorkAssessment) -> SocialWorkAssessmentOut:
    return SocialWorkAssessmentOut(
        id=record.id,
        admission_id=record.admission_id,
        social_worker_id=record.social_worker_id,
        assessment_date=str(record.assessment_date) if record.assessment_date else None,
        diagnostic_impression=record.diagnostic_impression,
        initial_assessment=record.initial_assessment,
        completion_status=record.completion_status or "pending",
    )


@router.get("/{admission_id}/social-work", response_model=SocialWorkAssessmentOut)
def get_social_work(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(SocialWorkAssessment)
        .filter(SocialWorkAssessment.admission_id == admission_id)
        .first()
    )
    if not record:
        return SocialWorkAssessmentOut(admission_id=admission_id)
    return _build_out(record)


@router.put("/{admission_id}/social-work", response_model=SocialWorkAssessmentOut)
def upsert_social_work(
    admission_id: int,
    data: SocialWorkAssessmentUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(SocialWorkAssessment)
        .filter(SocialWorkAssessment.admission_id == admission_id)
        .first()
    )
    assessment_date = date.fromisoformat(data.assessment_date) if data.assessment_date else None

    if record:
        record.assessment_date = assessment_date
        record.diagnostic_impression = data.diagnostic_impression
        record.initial_assessment = data.initial_assessment
        record.completion_status = data.completion_status
    else:
        record = SocialWorkAssessment(
            admission_id=admission_id,
            assessment_date=assessment_date,
            diagnostic_impression=data.diagnostic_impression,
            initial_assessment=data.initial_assessment,
            completion_status=data.completion_status,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return _build_out(record)
