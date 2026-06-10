from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.consent import PersonalItemsInventory
from app.models.user import User
from app.schemas.personal_items import PersonalItemsInventoryOut, PersonalItemsInventoryUpsert

router = APIRouter()


@router.get("/{admission_id}/personal-items", response_model=PersonalItemsInventoryOut)
def get_personal_items(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    inventory = (
        db.query(PersonalItemsInventory)
        .filter(PersonalItemsInventory.admission_id == admission_id)
        .first()
    )

    if not inventory:
        return PersonalItemsInventoryOut(admission_id=admission_id)

    return inventory


@router.put("/{admission_id}/personal-items", response_model=PersonalItemsInventoryOut)
def upsert_personal_items(
    admission_id: int,
    data: PersonalItemsInventoryUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    inventory = (
        db.query(PersonalItemsInventory)
        .filter(PersonalItemsInventory.admission_id == admission_id)
        .first()
    )

    items_data = [item.model_dump() for item in data.items]

    if inventory:
        inventory.items = items_data
        inventory.notes = data.notes
        inventory.recorded_by_user_id = current_user.id
    else:
        inventory = PersonalItemsInventory(
            admission_id=admission_id,
            items=items_data,
            notes=data.notes,
            recorded_by_user_id=current_user.id,
        )
        db.add(inventory)

    db.commit()
    db.refresh(inventory)
    return inventory
