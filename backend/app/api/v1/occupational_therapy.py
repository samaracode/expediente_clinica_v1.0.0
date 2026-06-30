from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, RoleRequired
from app.db.session import get_db
from app.models.admission import Admission
from app.models.assessment import OccupationalTherapyAssessment
from app.models.user import User
from app.schemas.occupational_therapy import (
    OccupationalTherapyAssessmentOut,
    OccupationalTherapyAssessmentUpsert,
)

router = APIRouter()
_role = RoleRequired(["admin", "occupational_therapist"])


def _build_out(record: OccupationalTherapyAssessment) -> OccupationalTherapyAssessmentOut:
    return OccupationalTherapyAssessmentOut(
        id=record.id,
        admission_id=record.admission_id,
        therapist_id=record.therapist_id,
        assessment_date=str(record.assessment_date) if record.assessment_date else None,
        initial_diagnostic_impression=record.initial_diagnostic_impression,
        occupational_profile=record.occupational_profile,
        completion_status=record.completion_status or "pending",
    )


@router.get("/{admission_id}/occupational-therapy", response_model=OccupationalTherapyAssessmentOut)
def get_occupational_therapy(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(OccupationalTherapyAssessment)
        .filter(OccupationalTherapyAssessment.admission_id == admission_id)
        .first()
    )
    if not record:
        return OccupationalTherapyAssessmentOut(admission_id=admission_id)
    return _build_out(record)


@router.put("/{admission_id}/occupational-therapy", response_model=OccupationalTherapyAssessmentOut)
def upsert_occupational_therapy(
    admission_id: int,
    data: OccupationalTherapyAssessmentUpsert,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    record = (
        db.query(OccupationalTherapyAssessment)
        .filter(OccupationalTherapyAssessment.admission_id == admission_id)
        .first()
    )
    assessment_date = date.fromisoformat(data.assessment_date) if data.assessment_date else None

    if record:
        record.assessment_date = assessment_date
        record.initial_diagnostic_impression = data.initial_diagnostic_impression
        record.occupational_profile = data.occupational_profile
        record.completion_status = data.completion_status
    else:
        record = OccupationalTherapyAssessment(
            admission_id=admission_id,
            assessment_date=assessment_date,
            initial_diagnostic_impression=data.initial_diagnostic_impression,
            occupational_profile=data.occupational_profile,
            completion_status=data.completion_status,
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return _build_out(record)
