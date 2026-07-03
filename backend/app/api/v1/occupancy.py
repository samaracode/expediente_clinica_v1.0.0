"""
Routers para el módulo de Ocupación + Lista de espera.

Rutas:
  GET  /occupancy                 — {capacity, occupied, available, by_status}
  GET  /waitlist                  — lista de espera (?status=)
  POST /waitlist                  — crear entrada
  PATCH /waitlist/{id}            — editar / cambiar estado
  GET  /settings/capacity         — leer capacidad
  PUT  /settings/capacity         — actualizar capacidad
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import ModuleRequired
from app.db.session import get_db
from app.models.occupancy import WaitlistStatus
from app.models.user import Module, User
from app.schemas.occupancy import (
    CapacityIn,
    CapacityOut,
    OccupancyOut,
    WaitlistEntryCreate,
    WaitlistEntryOut,
    WaitlistEntryPatch,
)
from app.services.occupancy_service import OccupancyService

_role = ModuleRequired(Module.operations)

# ─── Router: /occupancy ──────────────────────────────────────────────────────
occupancy_router = APIRouter()


@occupancy_router.get("", response_model=OccupancyOut)
def get_occupancy(
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """Tablero de ocupación: cupos totales, ocupados, disponibles y desglose por status."""
    return OccupancyService(db).get_occupancy()


# ─── Router: /waitlist ───────────────────────────────────────────────────────
waitlist_router = APIRouter()


@waitlist_router.get("", response_model=List[WaitlistEntryOut])
def list_waitlist(
    status: Optional[WaitlistStatus] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """Lista de espera, opcionalmente filtrada por status."""
    return OccupancyService(db).list_waitlist(status=status)


@waitlist_router.post("", response_model=WaitlistEntryOut, status_code=201)
def create_waitlist_entry(
    data: WaitlistEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(_role),
):
    """Agrega una persona a la lista de espera."""
    return OccupancyService(db).create_waitlist_entry(data, created_by_user_id=current_user.id)


@waitlist_router.patch("/{entry_id}", response_model=WaitlistEntryOut)
def patch_waitlist_entry(
    entry_id: int,
    data: WaitlistEntryPatch,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """Edita campos o cambia el status de una entrada de la lista de espera."""
    return OccupancyService(db).patch_waitlist_entry(entry_id, data)


# ─── Router: /settings (capacity) ────────────────────────────────────────────
settings_capacity_router = APIRouter()


@settings_capacity_router.get("/capacity", response_model=CapacityOut)
def get_capacity(
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """Lee la capacidad configurada del centro (default 24 si no está seteada)."""
    return OccupancyService(db).get_capacity()


@settings_capacity_router.put("/capacity", response_model=CapacityOut)
def set_capacity(
    data: CapacityIn,
    db: Session = Depends(get_db),
    _: User = Depends(_role),
):
    """Actualiza la capacidad del centro. Debe ser un entero positivo (> 0)."""
    return OccupancyService(db).set_capacity(data)
