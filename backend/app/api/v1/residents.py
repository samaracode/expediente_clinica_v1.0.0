from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import ModuleRequired, RoleRequired
from app.db.session import get_db
from app.models.user import Module, User
from app.schemas.resident import ResidentCreate, ResidentOut, ResidentPage, ResidentUpdate
from app.services.resident_service import ResidentService

_admin_only = RoleRequired(["admin"])
_role = ModuleRequired(Module.residents)

router = APIRouter()


def get_resident_service(db: Session = Depends(get_db)) -> ResidentService:
    return ResidentService(db)


@router.get("", response_model=ResidentPage)
def list_residents(
    q: Optional[str] = Query(None, description="Buscar por nombre o cédula"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    show_archived: bool = Query(False),
    service: ResidentService = Depends(get_resident_service),
    _: User = Depends(_role),
):
    return service.list_paginated(q, page, page_size, show_archived)


@router.post("", response_model=ResidentOut, status_code=status.HTTP_201_CREATED)
def create_resident(
    data: ResidentCreate,
    service: ResidentService = Depends(get_resident_service),
    _: User = Depends(_role),
):
    return service.create(data)


@router.get("/{resident_id}", response_model=ResidentOut)
def get_resident(
    resident_id: int,
    service: ResidentService = Depends(get_resident_service),
    _: User = Depends(_role),
):
    return service.get(resident_id)


@router.put("/{resident_id}", response_model=ResidentOut)
def update_resident(
    resident_id: int,
    data: ResidentUpdate,
    service: ResidentService = Depends(get_resident_service),
    _: User = Depends(_role),
):
    return service.update(resident_id, data)


@router.delete("/{resident_id}", status_code=204)
def archive_resident(
    resident_id: int,
    service: ResidentService = Depends(get_resident_service),
    _: User = Depends(_admin_only),
):
    service.archive(resident_id)
