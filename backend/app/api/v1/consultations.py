from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import RoleRequired, get_current_user, get_db
from app.schemas.consultations import ConsultationCreate, ConsultationOut, ConsultationUpdate
from app.services.consultation_service import ConsultationService

router = APIRouter()
_admin_only = RoleRequired(["admin"])


def get_consultation_service(db: Session = Depends(get_db)) -> ConsultationService:
    return ConsultationService(db)


@router.get("/{admission_id}/consultations", response_model=list[ConsultationOut])
def list_consultations(
    admission_id: int,
    area_id: Optional[int] = Query(None),
    service: ConsultationService = Depends(get_consultation_service),
    _: object = Depends(get_current_user),
):
    return service.list(admission_id, area_id)


@router.post("/{admission_id}/consultations", response_model=ConsultationOut, status_code=201)
def create_consultation(
    admission_id: int,
    body: ConsultationCreate,
    service: ConsultationService = Depends(get_consultation_service),
    _: object = Depends(get_current_user),
):
    return service.create(admission_id, body)


@router.put("/consultations/{consultation_id}", response_model=ConsultationOut)
def update_consultation(
    consultation_id: int,
    body: ConsultationUpdate,
    service: ConsultationService = Depends(get_consultation_service),
    _: object = Depends(get_current_user),
):
    return service.update(consultation_id, body)


@router.delete("/consultations/{consultation_id}", status_code=204)
def delete_consultation(
    consultation_id: int,
    service: ConsultationService = Depends(get_consultation_service),
    _: object = Depends(_admin_only),
):
    service.delete(consultation_id)
