from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user, get_db
from app.models.admission import Admission
from app.models.follow_up import Consultation
from app.models.user import Professional, TreatmentArea
from app.schemas.consultations import ConsultationOut, ConsultationCreate, ConsultationUpdate

router = APIRouter()


def _build_out(c: Consultation) -> ConsultationOut:
    professional_name = None
    if c.professional:
        professional_name = f"{c.professional.first_name} {c.professional.last_name}"
    area_name = c.area.name if c.area else None
    return ConsultationOut(
        id=c.id,
        admission_id=c.admission_id,
        professional_id=c.professional_id,
        area_id=c.area_id,
        consultation_type=c.consultation_type,
        description=c.description,
        observations=c.observations,
        consultation_date=str(c.consultation_date),
        next_appointment_date=str(c.next_appointment_date) if c.next_appointment_date else None,
        professional_name=professional_name,
        area_name=area_name,
    )


def _load(db: Session, consultation_id: int) -> Consultation:
    c = (
        db.query(Consultation)
        .options(
            joinedload(Consultation.professional),
            joinedload(Consultation.area),
        )
        .filter(Consultation.id == consultation_id)
        .first()
    )
    if not c:
        raise HTTPException(status_code=404, detail="Consulta no encontrada")
    return c


@router.get("/{admission_id}/consultations", response_model=list[ConsultationOut])
def list_consultations(
    admission_id: int,
    area_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")
    q = (
        db.query(Consultation)
        .options(joinedload(Consultation.professional), joinedload(Consultation.area))
        .filter(Consultation.admission_id == admission_id)
    )
    if area_id:
        q = q.filter(Consultation.area_id == area_id)
    return [_build_out(r) for r in q.order_by(Consultation.consultation_date.desc()).all()]


@router.post("/{admission_id}/consultations", response_model=ConsultationOut, status_code=201)
def create_consultation(
    admission_id: int,
    body: ConsultationCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    if not db.query(Admission).filter(Admission.id == admission_id).first():
        raise HTTPException(status_code=404, detail="Admisión no encontrada")

    consultation_date = date.fromisoformat(body.consultation_date)
    next_appt = date.fromisoformat(body.next_appointment_date) if body.next_appointment_date else None

    c = Consultation(
        admission_id=admission_id,
        consultation_date=consultation_date,
        next_appointment_date=next_appt,
        professional_id=body.professional_id,
        area_id=body.area_id,
        consultation_type=body.consultation_type,
        description=body.description,
        observations=body.observations,
    )
    db.add(c)
    db.commit()
    return _build_out(_load(db, c.id))


@router.put("/consultations/{consultation_id}", response_model=ConsultationOut)
def update_consultation(
    consultation_id: int,
    body: ConsultationUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    c = _load(db, consultation_id)

    if body.consultation_date is not None:
        c.consultation_date = date.fromisoformat(body.consultation_date)
    if body.next_appointment_date is not None:
        c.next_appointment_date = date.fromisoformat(body.next_appointment_date)
    if body.professional_id is not None:
        c.professional_id = body.professional_id
    if body.area_id is not None:
        c.area_id = body.area_id
    if body.consultation_type is not None:
        c.consultation_type = body.consultation_type
    if body.description is not None:
        c.description = body.description
    if body.observations is not None:
        c.observations = body.observations

    db.commit()
    return _build_out(_load(db, consultation_id))
