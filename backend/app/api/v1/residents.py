import math
import re
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.resident import Resident
from app.models.user import User
from app.schemas.resident import ResidentCreate, ResidentList, ResidentOut, ResidentUpdate, ResidentPage

router = APIRouter()


def _generate_code(db: Session) -> str:
    count = db.query(Resident).count()
    return f"ZOE-{count + 1:04d}"


@router.get("", response_model=ResidentPage)
def list_residents(
    q: Optional[str] = Query(None, description="Buscar por nombre o cédula"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Resident)
    if q:
        like = f"%{q}%"
        query = query.filter(
            Resident.first_name.ilike(like)
            | Resident.last_name.ilike(like)
            | Resident.id_number.ilike(like)
        )
    total = query.count()
    pages = max(1, math.ceil(total / page_size))
    items = query.order_by(Resident.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return ResidentPage(items=items, total=total, page=page, pages=pages)


@router.post("", response_model=ResidentOut, status_code=status.HTTP_201_CREATED)
def create_resident(
    data: ResidentCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if data.id_number and db.query(Resident).filter(Resident.id_number == data.id_number).first():
        raise HTTPException(status_code=400, detail="Ya existe un residente con esa cédula")
    resident = Resident(**data.model_dump(), code=_generate_code(db))
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return resident


@router.get("/{resident_id}", response_model=ResidentOut)
def get_resident(
    resident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return resident


@router.put("/{resident_id}", response_model=ResidentOut)
def update_resident(
    resident_id: int,
    data: ResidentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(resident, field, value)
    db.commit()
    db.refresh(resident)
    return resident
