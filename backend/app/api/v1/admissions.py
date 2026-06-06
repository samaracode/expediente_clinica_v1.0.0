from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.admission import Admission
from app.models.resident import Resident
from app.models.user import User
from app.schemas.admission import AdmissionCreate, AdmissionOut, AdmissionStatusUpdate

router = APIRouter()


def _generate_admission_number(db: Session) -> str:
    count = db.query(Admission).count()
    return f"ADM-{count + 1:05d}"


@router.post("", response_model=AdmissionOut, status_code=status.HTTP_201_CREATED)
def create_admission(
    data: AdmissionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Resident).filter(Resident.id == data.resident_id).first():
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    admission = Admission(**data.model_dump(), admission_number=_generate_admission_number(db))
    db.add(admission)
    db.commit()
    db.refresh(admission)
    return admission


@router.get("/{admission_id}", response_model=AdmissionOut)
def get_admission(
    admission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    return admission


@router.get("/resident/{resident_id}", response_model=List[AdmissionOut])
def get_resident_admissions(
    resident_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    if not db.query(Resident).filter(Resident.id == resident_id).first():
        raise HTTPException(status_code=404, detail="Residente no encontrado")
    return db.query(Admission).filter(Admission.resident_id == resident_id).order_by(Admission.created_at.desc()).all()


@router.put("/{admission_id}/status", response_model=AdmissionOut)
def update_admission_status(
    admission_id: int,
    data: AdmissionStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    admission = db.query(Admission).filter(Admission.id == admission_id).first()
    if not admission:
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    admission.status = data.status
    db.commit()
    db.refresh(admission)
    return admission
