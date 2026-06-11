from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.treatment import TreatmentPlanOut, TreatmentPlanUpsert
from app.services.treatment_service import TreatmentService

router = APIRouter()


def get_treatment_service(db: Session = Depends(get_db)) -> TreatmentService:
    return TreatmentService(db)


@router.get("/{admission_id}/treatment-plan", response_model=TreatmentPlanOut)
def get_treatment_plan(
    admission_id: int,
    service: TreatmentService = Depends(get_treatment_service),
    _: User = Depends(get_current_user),
):
    return service.get_plan(admission_id)


@router.put("/{admission_id}/treatment-plan", response_model=TreatmentPlanOut)
def upsert_treatment_plan(
    admission_id: int,
    data: TreatmentPlanUpsert,
    service: TreatmentService = Depends(get_treatment_service),
    current_user: User = Depends(get_current_user),
):
    return service.upsert_plan(admission_id, data, current_user)
