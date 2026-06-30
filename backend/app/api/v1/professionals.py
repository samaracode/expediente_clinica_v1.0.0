from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import RoleRequired, get_current_user
from app.db.session import get_db
from app.models.user import Professional, TreatmentArea, User
from app.schemas.admin import (
    ProfessionalCreate,
    ProfessionalOut,
    ProfessionalUpdate,
    TreatmentAreaOut,
)

router = APIRouter()

_admin_only = RoleRequired(["admin"])


def _build_out(p: Professional) -> ProfessionalOut:
    return ProfessionalOut(
        id=p.id,
        user_id=p.user_id,
        area_id=p.area_id,
        first_name=p.first_name,
        last_name=p.last_name,
        specialty=p.specialty,
        is_active=p.is_active,
        area_name=p.area.name if p.area else None,
        user_email=p.user.email if p.user else None,
    )


@router.get("/areas", response_model=List[TreatmentAreaOut])
def list_areas(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    areas = db.query(TreatmentArea).order_by(TreatmentArea.name).all()
    return areas


@router.get("/", response_model=List[ProfessionalOut])
def list_professionals(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    professionals = (
        db.query(Professional)
        .options(joinedload(Professional.area), joinedload(Professional.user))
        .order_by(Professional.last_name)
        .all()
    )
    return [_build_out(p) for p in professionals]


@router.post("/", response_model=ProfessionalOut, status_code=201)
def create_professional(
    data: ProfessionalCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    if not db.query(User).filter(User.id == data.user_id).first():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not db.query(TreatmentArea).filter(TreatmentArea.id == data.area_id).first():
        raise HTTPException(status_code=404, detail="Área no encontrada")
    if db.query(Professional).filter(Professional.user_id == data.user_id).first():
        raise HTTPException(status_code=400, detail="Este usuario ya tiene un perfil de profesional")

    prof = Professional(
        user_id=data.user_id,
        area_id=data.area_id,
        first_name=data.first_name,
        last_name=data.last_name,
        specialty=data.specialty,
        is_active=True,
    )
    db.add(prof)
    db.commit()
    db.refresh(prof)

    prof = (
        db.query(Professional)
        .options(joinedload(Professional.area), joinedload(Professional.user))
        .filter(Professional.id == prof.id)
        .first()
    )
    return _build_out(prof)


@router.put("/{prof_id}", response_model=ProfessionalOut)
def update_professional(
    prof_id: int,
    data: ProfessionalUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    prof = (
        db.query(Professional)
        .options(joinedload(Professional.area), joinedload(Professional.user))
        .filter(Professional.id == prof_id)
        .first()
    )
    if not prof:
        raise HTTPException(status_code=404, detail="Profesional no encontrado")

    if data.area_id is not None:
        if not db.query(TreatmentArea).filter(TreatmentArea.id == data.area_id).first():
            raise HTTPException(status_code=404, detail="Área no encontrada")
        prof.area_id = data.area_id
    if data.first_name is not None:
        prof.first_name = data.first_name
    if data.last_name is not None:
        prof.last_name = data.last_name
    if data.specialty is not None:
        prof.specialty = data.specialty
    if data.is_active is not None:
        prof.is_active = data.is_active

    db.commit()
    db.refresh(prof)

    prof = (
        db.query(Professional)
        .options(joinedload(Professional.area), joinedload(Professional.user))
        .filter(Professional.id == prof_id)
        .first()
    )
    return _build_out(prof)
