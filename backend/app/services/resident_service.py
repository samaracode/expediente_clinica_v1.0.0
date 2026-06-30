import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resident import Resident
from app.schemas.resident import ResidentCreate, ResidentPage, ResidentUpdate


class ResidentService:
    def __init__(self, db: Session):
        self.db = db

    def _generate_code(self) -> str:
        count = self.db.query(Resident).count()
        return f"ZOE-{count + 1:04d}"

    def _get_or_404(self, resident_id: int) -> Resident:
        resident = self.db.query(Resident).filter(Resident.id == resident_id).first()
        if not resident:
            raise HTTPException(status_code=404, detail="Residente no encontrado")
        return resident

    def list_paginated(
        self,
        q: Optional[str],
        page: int,
        page_size: int,
        show_archived: bool,
    ) -> ResidentPage:
        query = self.db.query(Resident)
        if not show_archived:
            query = query.filter(Resident.is_deleted == False)  # noqa: E712
        if q:
            like = f"%{q}%"
            query = query.filter(
                Resident.first_name.ilike(like)
                | Resident.last_name.ilike(like)
                | Resident.id_number.ilike(like)
            )
        total = query.count()
        pages = max(1, math.ceil(total / page_size))
        items = (
            query.order_by(Resident.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return ResidentPage(items=items, total=total, page=page, pages=pages)

    def get(self, resident_id: int) -> Resident:
        return self._get_or_404(resident_id)

    def create(self, data: ResidentCreate) -> Resident:
        if data.id_number and self.db.query(Resident).filter(
            Resident.id_number == data.id_number
        ).first():
            raise HTTPException(
                status_code=400, detail="Ya existe un residente con esa cédula"
            )
        resident = Resident(**data.model_dump(), code=self._generate_code())
        self.db.add(resident)
        self.db.commit()
        self.db.refresh(resident)
        return resident

    def update(self, resident_id: int, data: ResidentUpdate) -> Resident:
        resident = self._get_or_404(resident_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(resident, field, value)
        self.db.commit()
        self.db.refresh(resident)
        return resident

    def archive(self, resident_id: int) -> None:
        resident = self._get_or_404(resident_id)
        resident.is_deleted = True
        resident.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
