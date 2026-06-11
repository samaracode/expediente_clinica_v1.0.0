from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import RoleRequired, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.admission import AdmissionCreate, AdmissionOut, AdmissionStatusUpdate
from app.services.admission_service import AdmissionService

router = APIRouter()
_admin_only = RoleRequired(["admin"])


def get_admission_service(db: Session = Depends(get_db)) -> AdmissionService:
    return AdmissionService(db)


@router.post("", response_model=AdmissionOut, status_code=status.HTTP_201_CREATED)
def create_admission(
    data: AdmissionCreate,
    service: AdmissionService = Depends(get_admission_service),
    _: User = Depends(get_current_user),
):
    return service.create(data)


@router.get("/{admission_id}", response_model=AdmissionOut)
def get_admission(
    admission_id: int,
    service: AdmissionService = Depends(get_admission_service),
    _: User = Depends(get_current_user),
):
    return service.get(admission_id)


@router.get("/resident/{resident_id}", response_model=List[AdmissionOut])
def get_resident_admissions(
    resident_id: int,
    service: AdmissionService = Depends(get_admission_service),
    _: User = Depends(get_current_user),
):
    return service.list_by_resident(resident_id)


@router.delete("/{admission_id}", status_code=204)
def archive_admission(
    admission_id: int,
    service: AdmissionService = Depends(get_admission_service),
    _: User = Depends(_admin_only),
):
    service.archive(admission_id)


@router.put("/{admission_id}/status", response_model=AdmissionOut)
def update_admission_status(
    admission_id: int,
    data: AdmissionStatusUpdate,
    service: AdmissionService = Depends(get_admission_service),
    _: User = Depends(get_current_user),
):
    return service.update_status(admission_id, data)
