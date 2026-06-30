"""
Router para alergias de residentes.

Rutas:
  GET    /residents/{resident_id}/allergies
  POST   /residents/{resident_id}/allergies
  DELETE /residents/{resident_id}/allergies/{allergy_id}
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.medication import ResidentAllergyCreate, ResidentAllergyOut
from app.services.medication_service import ResidentAllergyService

router = APIRouter()


@router.get("/{resident_id}/allergies", response_model=List[ResidentAllergyOut])
def list_allergies(
    resident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ResidentAllergyService(db).list(resident_id)


@router.post("/{resident_id}/allergies", response_model=ResidentAllergyOut, status_code=201)
def create_allergy(
    resident_id: int,
    data: ResidentAllergyCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return ResidentAllergyService(db).create(resident_id, data)


@router.delete("/{resident_id}/allergies/{allergy_id}", status_code=204)
def delete_allergy(
    resident_id: int,
    allergy_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    ResidentAllergyService(db).delete(resident_id, allergy_id)
