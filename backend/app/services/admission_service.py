from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.admission import Admission
from app.models.resident import Resident
from app.schemas.admission import AdmissionCreate, AdmissionStatusUpdate


class AdmissionService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_admission_number(self) -> str:
        count = self.db.query(Admission).count()
        return f"ADM-{count + 1:05d}"

    def _get_or_404(self, admission_id: int) -> Admission:
        admission = self.db.query(Admission).filter(Admission.id == admission_id).first()
        if not admission:
            raise HTTPException(status_code=404, detail="Admisión no encontrada")
        return admission

    def create(self, data: AdmissionCreate) -> Admission:
        if not self.db.query(Resident).filter(Resident.id == data.resident_id).first():
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        admission = Admission(
            **data.model_dump(),
            admission_number=self._generate_admission_number(),
        )
        self.db.add(admission)
        self.db.commit()
        self.db.refresh(admission)
        return admission

    def get(self, admission_id: int) -> Admission:
        return self._get_or_404(admission_id)

    def list_by_resident(self, resident_id: int) -> List[Admission]:
        if not self.db.query(Resident).filter(Resident.id == resident_id).first():
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return (
            self.db.query(Admission)
            .filter(
                Admission.resident_id == resident_id,
                Admission.is_deleted == False,  # noqa: E712
            )
            .order_by(Admission.created_at.desc())
            .all()
        )

    def archive(self, admission_id: int) -> None:
        admission = self._get_or_404(admission_id)
        admission.is_deleted = True
        admission.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def update_status(self, admission_id: int, data: AdmissionStatusUpdate) -> Admission:
        admission = self._get_or_404(admission_id)
        admission.status = data.status
        self.db.commit()
        self.db.refresh(admission)
        return admission
