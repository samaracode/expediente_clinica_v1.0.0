from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.resident import Resident, Relative, PatientRelative
from app.schemas.relatives import RelativeOut, RelativeCreate, RelativeUpdate

router = APIRouter()


def _build_out(pr: PatientRelative) -> RelativeOut:
    r = pr.relative
    return RelativeOut(
        id=r.id,
        patient_relative_id=pr.id,
        relation_type=pr.relation_type,
        id_number=r.id_number,
        first_name=r.first_name,
        last_name=r.last_name,
        birthdate=str(r.birthdate) if r.birthdate else None,
        marital_status=r.marital_status.value if r.marital_status else None,
        address=r.address,
        judicial_situation=r.judicial_situation,
        phone=r.phone,
        education_level=r.education_level.value if r.education_level else None,
    )


def _load_pr(db: Session, patient_relative_id: int) -> PatientRelative:
    pr = (
        db.query(PatientRelative)
        .options(joinedload(PatientRelative.relative))
        .filter(PatientRelative.id == patient_relative_id)
        .first()
    )
    if not pr:
        raise HTTPException(status_code=404, detail="Familiar no encontrado")
    return pr


@router.get("/{resident_id}/relatives", response_model=list[RelativeOut])
def list_relatives(
    resident_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    if not db.query(Resident).filter(Resident.id == resident_id).first():
        raise HTTPException(status_code=404, detail="Residente no encontrado")

    rows = (
        db.query(PatientRelative)
        .options(joinedload(PatientRelative.relative))
        .filter(PatientRelative.resident_id == resident_id)
        .all()
    )
    return [_build_out(pr) for pr in rows]


@router.post("/{resident_id}/relatives", response_model=RelativeOut, status_code=201)
def create_relative(
    resident_id: int,
    body: RelativeCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    if not db.query(Resident).filter(Resident.id == resident_id).first():
        raise HTTPException(status_code=404, detail="Residente no encontrado")

    # If id_number provided, check if this relative already exists (reuse)
    existing_relative = None
    if body.id_number:
        existing_relative = db.query(Relative).filter(Relative.id_number == body.id_number).first()

    if existing_relative:
        rel = existing_relative
    else:
        rel = Relative(
            id_number=body.id_number,
            first_name=body.first_name,
            last_name=body.last_name,
            birthdate=date.fromisoformat(body.birthdate) if body.birthdate else None,
            marital_status=body.marital_status,
            address=body.address,
            judicial_situation=body.judicial_situation,
            phone=body.phone,
            education_level=body.education_level,
        )
        db.add(rel)
        db.flush()

    # Avoid duplicate link
    existing_link = (
        db.query(PatientRelative)
        .filter(PatientRelative.resident_id == resident_id, PatientRelative.relative_id == rel.id)
        .first()
    )
    if existing_link:
        raise HTTPException(status_code=409, detail="Este familiar ya está vinculado al residente")

    pr = PatientRelative(resident_id=resident_id, relative_id=rel.id, relation_type=body.relation_type)
    db.add(pr)
    db.commit()
    return _build_out(_load_pr(db, pr.id))


@router.delete("/relatives/{patient_relative_id}", status_code=204)
def unlink_relative(
    patient_relative_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    pr = db.query(PatientRelative).filter(PatientRelative.id == patient_relative_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Familiar no encontrado")
    db.delete(pr)
    db.commit()


@router.put("/relatives/{patient_relative_id}", response_model=RelativeOut)
def update_relative(
    patient_relative_id: int,
    body: RelativeUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    pr = _load_pr(db, patient_relative_id)
    r = pr.relative

    if body.relation_type is not None:
        pr.relation_type = body.relation_type
    if body.first_name is not None:
        r.first_name = body.first_name
    if body.last_name is not None:
        r.last_name = body.last_name
    if body.id_number is not None:
        r.id_number = body.id_number
    if body.birthdate is not None:
        r.birthdate = date.fromisoformat(body.birthdate)
    if body.marital_status is not None:
        r.marital_status = body.marital_status
    if body.address is not None:
        r.address = body.address
    if body.judicial_situation is not None:
        r.judicial_situation = body.judicial_situation
    if body.phone is not None:
        r.phone = body.phone
    if body.education_level is not None:
        r.education_level = body.education_level

    db.commit()
    return _build_out(_load_pr(db, patient_relative_id))
