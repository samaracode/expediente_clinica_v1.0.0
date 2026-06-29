"""
Router para configuración de franjas horarias de medicamentos.

Rutas:
  GET /settings/medication-slots  — listar franjas
  PUT /settings/medication-slots  — reemplazar lista completa de franjas
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.medication import MedTimeSlotOut, MedTimeSlotUpdate
from app.services.medication_service import MedTimeSlotsService

router = APIRouter()


@router.get("/medication-slots", response_model=List[MedTimeSlotOut])
def list_slots(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return MedTimeSlotsService(db).list()


@router.put("/medication-slots", response_model=List[MedTimeSlotOut])
def put_slots(
    slots: List[MedTimeSlotUpdate],
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return MedTimeSlotsService(db).put(slots)
