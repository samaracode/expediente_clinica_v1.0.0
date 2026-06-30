from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, RoleRequired
from app.db.session import get_db
from app.models.admission import Admission
from app.models.assessment import PsychologyAssessment
from app.models.user import User
from app.schemas.psychology import PsychologyAssessmentOut, PsychologyAssessmentUpsert

router = APIRouter()
_role = RoleRequired(["admin", "psychologist"])


def _build_out(record: PsychologyAssessment) -> PsychologyAssessmentOut:
    return PsychologyAssessmentOut(
        id=record.id,
        admission_id=record.admission_id,
        psychologist_id=record.psychologist_id,
        assessment_date=str(record.assessment_date) if record.assessment_date else None,
        initial_diagnostic_impression=record.initial_diagnostic_impression,
        observable_assessment=record.observable_assessment,
        diagnostic_tests_notes=(record.diagnostic_tests or {}).get("notes"),
        completion_status=record.completion_status or "pending",
    )


@router.get("/{admission_id}/psychology", response_model=PsychologyAssessmentOut)
def get_psychology(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(PsychologyAssessment)
        .filter(PsychologyAssessment.admission_id == admission_id)
        .first()
    )
    if not record:
        return PsychologyAssessmentOut(admission_id=admission_id)
    return _build_out(record)


@router.put("/{admission_id}/psychology", response_model=PsychologyAssessmentOut)
def upsert_psychology(
    admission_id: int,
    data: PsychologyAssessmentUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(PsychologyAssessment)
        .filter(PsychologyAssessment.admission_id == admission_id)
        .first()
    )
    assessment_date = date.fromisoformat(data.assessment_date) if data.assessment_date else None
    diagnostic_tests = {"notes": data.diagnostic_tests_notes} if data.diagnostic_tests_notes else None

    if record:
        record.assessment_date = assessment_date
        record.initial_diagnostic_impression = data.initial_diagnostic_impression
        record.observable_assessment = data.observable_assessment
        record.diagnostic_tests = diagnostic_tests
        record.completion_status = data.completion_status
    else:
        record = PsychologyAssessment(
            admission_id=admission_id,
            assessment_date=assessment_date,
            initial_diagnostic_impression=data.initial_diagnostic_impression,
            observable_assessment=data.observable_assessment,
            diagnostic_tests=diagnostic_tests,
            completion_status=data.completion_status,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return _build_out(record)
