from datetime import date, datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.admission import Admission
from app.models.follow_up import Consultation
from app.schemas.consultations import ConsultationCreate, ConsultationOut, ConsultationUpdate


class ConsultationService:
    def __init__(self, db: Session):
        self.db = db

    def _build_out(self, c: Consultation) -> ConsultationOut:
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

    def _load(self, consultation_id: int) -> Consultation:
        c = (
            self.db.query(Consultation)
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

    def list(self, admission_id: int, area_id: Optional[int] = None) -> List[ConsultationOut]:
        if not self.db.query(Admission).filter(Admission.id == admission_id).first():
            raise HTTPException(status_code=404, detail="Admisión no encontrada")
        q = (
            self.db.query(Consultation)
            .options(joinedload(Consultation.professional), joinedload(Consultation.area))
            .filter(
                Consultation.admission_id == admission_id,
                Consultation.is_deleted == False,  # noqa: E712
            )
        )
        if area_id:
            q = q.filter(Consultation.area_id == area_id)
        return [self._build_out(r) for r in q.order_by(Consultation.consultation_date.desc()).all()]

    def create(self, admission_id: int, body: ConsultationCreate) -> ConsultationOut:
        if not self.db.query(Admission).filter(Admission.id == admission_id).first():
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
        self.db.add(c)
        self.db.commit()
        return self._build_out(self._load(c.id))

    def update(self, consultation_id: int, body: ConsultationUpdate) -> ConsultationOut:
        c = self._load(consultation_id)
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
        self.db.commit()
        return self._build_out(self._load(consultation_id))

    def delete(self, consultation_id: int) -> None:
        c = self.db.query(Consultation).filter(Consultation.id == consultation_id).first()
        if not c:
            raise HTTPException(status_code=404, detail="Consulta no encontrada")
        c.is_deleted = True
        c.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
