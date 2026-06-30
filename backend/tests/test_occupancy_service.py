"""
Tests para el módulo de Ocupación + Lista de espera — Fase 3.

Cubren:
- Ocupación cuenta solo admisiones en statuses activos
  (consents_pending, assessment_in_progress, treatment_active).
- intake_pending / discharged / abandoned NO cuentan como ocupadas.
- by_status desglosa correctamente por status.
- available = capacity - occupied.
- Capacity: default 24, PUT lo cambia, GET refleja el nuevo valor.
- PUT con valor <= 0 → 422 (validación Pydantic).
- CRUD de waitlist: POST crea, GET lista, PATCH cambia campos y status.
- Filtro ?status= en GET /waitlist.
- PATCH sobre entry inexistente → 404.
"""

import pytest
from datetime import date

from fastapi import HTTPException

from app.models.admission import AdmissionStatus
from app.models.occupancy import WaitlistStatus
from app.schemas.occupancy import (
    CapacityIn,
    WaitlistEntryCreate,
    WaitlistEntryPatch,
)
from app.services.occupancy_service import DEFAULT_CAPACITY, OccupancyService


# ---------------------------------------------------------------------------
# Ocupación
# ---------------------------------------------------------------------------

class TestOccupancy:
    def test_empty_db_shows_zero_occupied(self, db):
        """Sin admisiones, occupied = 0 y available = capacity default."""
        svc = OccupancyService(db)
        result = svc.get_occupancy()
        assert result.occupied == 0
        assert result.capacity == DEFAULT_CAPACITY
        assert result.available == DEFAULT_CAPACITY

    def test_only_active_statuses_counted(self, db, make_admission):
        """Solo los tres statuses activos cuentan como ocupados."""
        make_admission(status=AdmissionStatus.consents_pending)
        make_admission(status=AdmissionStatus.assessment_in_progress)
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = OccupancyService(db)
        result = svc.get_occupancy()
        assert result.occupied == 3

    def test_inactive_statuses_not_counted(self, db, make_admission):
        """intake_pending, discharged y abandoned NO cuentan como ocupados."""
        make_admission(status=AdmissionStatus.intake_pending)
        make_admission(status=AdmissionStatus.discharged)
        make_admission(status=AdmissionStatus.abandoned)
        db.commit()

        svc = OccupancyService(db)
        result = svc.get_occupancy()
        assert result.occupied == 0

    def test_mixed_statuses_correct_count(self, db, make_admission):
        """Mezcla de statuses activos e inactivos: solo cuentan los activos."""
        make_admission(status=AdmissionStatus.treatment_active)
        make_admission(status=AdmissionStatus.consents_pending)
        make_admission(status=AdmissionStatus.intake_pending)  # no cuenta
        make_admission(status=AdmissionStatus.discharged)       # no cuenta
        db.commit()

        svc = OccupancyService(db)
        result = svc.get_occupancy()
        assert result.occupied == 2
        assert result.available == DEFAULT_CAPACITY - 2

    def test_by_status_breakdown(self, db, make_admission):
        """by_status refleja el conteo por cada status activo."""
        make_admission(status=AdmissionStatus.consents_pending)
        make_admission(status=AdmissionStatus.consents_pending)
        make_admission(status=AdmissionStatus.assessment_in_progress)
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = OccupancyService(db)
        result = svc.get_occupancy()
        assert result.by_status["consents_pending"] == 2
        assert result.by_status["assessment_in_progress"] == 1
        assert result.by_status["treatment_active"] == 1
        assert result.occupied == 4

    def test_available_never_negative(self, db, make_admission):
        """Si occupied > capacity, available = 0 (no negativo)."""
        svc = OccupancyService(db)
        # Primero setear capacidad = 1
        svc.set_capacity(CapacityIn(capacity=1))

        make_admission(status=AdmissionStatus.treatment_active)
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        result = svc.get_occupancy()
        assert result.occupied == 2
        assert result.available == 0  # max(1-2, 0) = 0


# ---------------------------------------------------------------------------
# Capacity settings
# ---------------------------------------------------------------------------

class TestCapacity:
    def test_get_capacity_default(self, db):
        """Sin setting persistido, la capacidad es DEFAULT_CAPACITY (24)."""
        svc = OccupancyService(db)
        result = svc.get_capacity()
        assert result.capacity == DEFAULT_CAPACITY

    def test_set_capacity_changes_value(self, db):
        """PUT /settings/capacity actualiza el valor y GET lo refleja."""
        svc = OccupancyService(db)
        svc.set_capacity(CapacityIn(capacity=30))
        result = svc.get_capacity()
        assert result.capacity == 30

    def test_set_capacity_updates_occupancy(self, db, make_admission):
        """Cambiar la capacidad afecta el available en /occupancy."""
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = OccupancyService(db)
        svc.set_capacity(CapacityIn(capacity=10))

        result = svc.get_occupancy()
        assert result.capacity == 10
        assert result.occupied == 1
        assert result.available == 9

    def test_set_capacity_upsert(self, db):
        """PUT /settings/capacity es un upsert: puede llamarse múltiples veces."""
        svc = OccupancyService(db)
        svc.set_capacity(CapacityIn(capacity=20))
        svc.set_capacity(CapacityIn(capacity=25))
        result = svc.get_capacity()
        assert result.capacity == 25

    def test_capacity_zero_raises_validation_error(self):
        """Capacidad = 0 falla la validación de CapacityIn (Pydantic)."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CapacityIn(capacity=0)

    def test_capacity_negative_raises_validation_error(self):
        """Capacidad negativa falla la validación de CapacityIn (Pydantic)."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            CapacityIn(capacity=-5)


# ---------------------------------------------------------------------------
# Waitlist CRUD
# ---------------------------------------------------------------------------

class TestWaitlistCRUD:
    def test_create_entry(self, db, make_user):
        """POST /waitlist crea una entrada con status=waiting."""
        user = make_user()
        db.commit()

        svc = OccupancyService(db)
        data = WaitlistEntryCreate(
            full_name="María López",
            contact_phone="8888-0000",
            referred_by="Hospital Nacional",
        )
        result = svc.create_waitlist_entry(data, created_by_user_id=user.id)

        assert result.id is not None
        assert result.full_name == "María López"
        assert result.contact_phone == "8888-0000"
        assert result.status == WaitlistStatus.waiting
        assert result.created_by_user_id == user.id

    def test_create_entry_sets_requested_at_today_if_none(self, db):
        """Si no se especifica requested_at, queda como la fecha de hoy."""
        svc = OccupancyService(db)
        result = svc.create_waitlist_entry(
            WaitlistEntryCreate(full_name="Sin fecha"),
            created_by_user_id=None,
        )
        assert result.requested_at == date.today()

    def test_list_entries(self, db):
        """GET /waitlist devuelve todas las entradas."""
        svc = OccupancyService(db)
        svc.create_waitlist_entry(WaitlistEntryCreate(full_name="A"), created_by_user_id=None)
        svc.create_waitlist_entry(WaitlistEntryCreate(full_name="B"), created_by_user_id=None)

        result = svc.list_waitlist()
        assert len(result) == 2

    def test_list_entries_empty(self, db):
        """Sin entradas, GET /waitlist devuelve lista vacía."""
        svc = OccupancyService(db)
        assert svc.list_waitlist() == []

    def test_patch_status(self, db):
        """PATCH /waitlist/{id} cambia el status de la entrada."""
        svc = OccupancyService(db)
        entry = svc.create_waitlist_entry(
            WaitlistEntryCreate(full_name="Carlos"),
            created_by_user_id=None,
        )
        assert entry.status == WaitlistStatus.waiting

        updated = svc.patch_waitlist_entry(
            entry.id,
            WaitlistEntryPatch(status=WaitlistStatus.admitted),
        )
        assert updated.status == WaitlistStatus.admitted
        assert updated.full_name == "Carlos"  # no cambió

    def test_patch_fields(self, db):
        """PATCH actualiza solo los campos enviados (partial update)."""
        svc = OccupancyService(db)
        entry = svc.create_waitlist_entry(
            WaitlistEntryCreate(full_name="Inicial", contact_phone="1111"),
            created_by_user_id=None,
        )

        updated = svc.patch_waitlist_entry(
            entry.id,
            WaitlistEntryPatch(full_name="Actualizado"),
        )
        assert updated.full_name == "Actualizado"
        assert updated.contact_phone == "1111"  # no cambió

    def test_patch_not_found_raises_404(self, db):
        """PATCH sobre entrada inexistente → HTTPException 404."""
        svc = OccupancyService(db)
        with pytest.raises(HTTPException) as exc:
            svc.patch_waitlist_entry(9999, WaitlistEntryPatch(status=WaitlistStatus.cancelled))
        assert exc.value.status_code == 404

    def test_patch_all_statuses(self, db):
        """Se puede cambiar a cualquier status del enum."""
        svc = OccupancyService(db)
        entry = svc.create_waitlist_entry(
            WaitlistEntryCreate(full_name="Test"), created_by_user_id=None
        )
        for status in [WaitlistStatus.admitted, WaitlistStatus.declined, WaitlistStatus.cancelled, WaitlistStatus.waiting]:
            updated = svc.patch_waitlist_entry(entry.id, WaitlistEntryPatch(status=status))
            assert updated.status == status


# ---------------------------------------------------------------------------
# Filtro ?status= en GET /waitlist
# ---------------------------------------------------------------------------

class TestWaitlistFilter:
    def test_filter_by_status_waiting(self, db):
        """GET /waitlist?status=waiting devuelve solo las entradas en espera."""
        svc = OccupancyService(db)
        e1 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="En espera"), created_by_user_id=None)
        e2 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="Admitido"), created_by_user_id=None)
        svc.patch_waitlist_entry(e2.id, WaitlistEntryPatch(status=WaitlistStatus.admitted))

        result = svc.list_waitlist(status=WaitlistStatus.waiting)
        ids = [r.id for r in result]
        assert e1.id in ids
        assert e2.id not in ids

    def test_filter_by_status_admitted(self, db):
        """GET /waitlist?status=admitted devuelve solo las admitidas."""
        svc = OccupancyService(db)
        e1 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="A"), created_by_user_id=None)
        e2 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="B"), created_by_user_id=None)
        svc.patch_waitlist_entry(e1.id, WaitlistEntryPatch(status=WaitlistStatus.admitted))

        result = svc.list_waitlist(status=WaitlistStatus.admitted)
        assert len(result) == 1
        assert result[0].id == e1.id

    def test_filter_no_status_returns_all(self, db):
        """Sin filtro, GET /waitlist devuelve todas (independiente del status)."""
        svc = OccupancyService(db)
        e1 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="A"), created_by_user_id=None)
        e2 = svc.create_waitlist_entry(WaitlistEntryCreate(full_name="B"), created_by_user_id=None)
        svc.patch_waitlist_entry(e2.id, WaitlistEntryPatch(status=WaitlistStatus.declined))

        result = svc.list_waitlist()
        assert len(result) == 2

    def test_filter_returns_empty_if_none_match(self, db):
        """Filtro que no coincide con nada → lista vacía."""
        svc = OccupancyService(db)
        svc.create_waitlist_entry(WaitlistEntryCreate(full_name="Solo espera"), created_by_user_id=None)

        result = svc.list_waitlist(status=WaitlistStatus.cancelled)
        assert result == []
