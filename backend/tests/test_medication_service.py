"""
Tests para el módulo de Medicamentos (MAR) — Fase 1B.

Cubren:
- Catálogo: crear y listar medicamentos.
- Órdenes: crear y listar por admisión; orden inválida (medication 404).
- Pase: generación lazy idempotente (no duplica al llamar dos veces).
- Record: taken OK; refused sin reason → 400; omitted sin reason → 400;
          controlado sin witness → 400.
- PRN: sin reason → 400; con reason OK.
- Flag is_overdue.
- Alergias: CRUD completo (GET, POST, DELETE).
- Franjas horarias: GET y PUT.
- Patch de orden (cambio de status).
"""

import pytest
from datetime import date, datetime, time, timedelta, timezone
from fastapi import HTTPException

from app.models.medication import (
    AdministrationStatus,
    MedTimeSlot,
    Medication,
    MedicationAdministration,
    MedicationOrder,
    OrderStatus,
    ScheduleType,
    ResidentAllergy,
)
from app.models.admission import AdmissionStatus
from app.schemas.medication import (
    AdministrationRecord,
    MedTimeSlotUpdate,
    MedicationCreate,
    MedicationOrderCreate,
    MedicationOrderPatch,
    MedicationUpdate,
    PRNRecord,
    ResidentAllergyCreate,
)
from app.services.medication_service import (
    AdministrationService,
    DailyPassService,
    MedTimeSlotsService,
    MedicationCatalogService,
    MedicationOrderService,
    ResidentAllergyService,
)


# ---------------------------------------------------------------------------
# Fixtures auxiliares para este módulo
# ---------------------------------------------------------------------------

@pytest.fixture
def make_medication(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {
            "name": f"Medicamento {counter['n']}",
            "is_controlled": False,
        }
        defaults.update(kwargs)
        med = Medication(**defaults)
        db.add(med)
        db.flush()
        return med

    return _make


@pytest.fixture
def make_slot(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {
            "label": f"Franja {counter['n']}",
            "time": time(6 + counter["n"], 0),
            "sort_order": counter["n"],
        }
        defaults.update(kwargs)
        slot = MedTimeSlot(**defaults)
        db.add(slot)
        db.flush()
        return slot

    return _make


@pytest.fixture
def make_order(db, make_admission, make_medication):
    """Crea una MedicationOrder usando fixtures existentes."""
    counter = {"n": 0}

    def _make(admission=None, medication=None, **kwargs):
        counter["n"] += 1
        if admission is None:
            admission = make_admission()
        if medication is None:
            medication = make_medication()
        defaults = {
            "admission_id": admission.id,
            "medication_id": medication.id,
            "dose": "1 tableta",
            "route": "oral",
            "schedule_type": ScheduleType.scheduled,
            "start_date": date(2024, 1, 1),
            "status": OrderStatus.active,
            "is_controlled": False,
        }
        defaults.update(kwargs)
        order = MedicationOrder(**defaults)
        db.add(order)
        db.flush()
        return order

    return _make


@pytest.fixture
def make_administration(db, make_order):
    def _make(order=None, **kwargs):
        if order is None:
            order = make_order()
        defaults = {
            "order_id": order.id,
            "admission_id": order.admission_id,
            "status": AdministrationStatus.pending,
        }
        defaults.update(kwargs)
        adm = MedicationAdministration(**defaults)
        db.add(adm)
        db.flush()
        return adm

    return _make


# ---------------------------------------------------------------------------
# Catálogo
# ---------------------------------------------------------------------------

class TestMedicationCatalog:
    def test_create_returns_medication(self, db):
        data = MedicationCreate(name="Diazepam", is_controlled=True, strength="5 mg")
        result = MedicationCatalogService(db).create(data)
        assert result.id is not None
        assert result.name == "Diazepam"
        assert result.is_controlled is True

    def test_list_returns_all(self, db, make_medication):
        make_medication(name="Alpha")
        make_medication(name="Beta")
        result = MedicationCatalogService(db).list()
        names = [r.name for r in result]
        assert "Alpha" in names
        assert "Beta" in names

    def test_list_empty(self, db):
        result = MedicationCatalogService(db).list()
        assert result == []

    def test_update_changes_fields(self, db, make_medication):
        med = make_medication(name="Original", is_controlled=False)
        result = MedicationCatalogService(db).update(
            med.id, MedicationUpdate(name="Actualizado", is_controlled=True)
        )
        assert result.name == "Actualizado"
        assert result.is_controlled is True

    def test_update_partial_keeps_other_fields(self, db, make_medication):
        med = make_medication(name="Original", strength="5 mg")
        result = MedicationCatalogService(db).update(med.id, MedicationUpdate(strength="10 mg"))
        assert result.name == "Original"
        assert result.strength == "10 mg"

    def test_update_not_found_raises_404(self, db):
        with pytest.raises(HTTPException) as exc:
            MedicationCatalogService(db).update(9999, MedicationUpdate(name="X"))
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Órdenes
# ---------------------------------------------------------------------------

class TestMedicationOrders:
    def test_create_order(self, db, make_admission, make_medication):
        admission = make_admission()
        med = make_medication()
        data = MedicationOrderCreate(
            admission_id=admission.id,
            medication_id=med.id,
            dose="2 tabletas",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            start_date=date(2024, 1, 1),
        )
        result = MedicationOrderService(db).create(admission.id, data)
        assert result.id is not None
        assert result.dose == "2 tabletas"
        assert result.status == OrderStatus.active

    def test_create_order_admission_not_found(self, db, make_medication):
        med = make_medication()
        data = MedicationOrderCreate(
            admission_id=9999,
            medication_id=med.id,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.prn,
            start_date=date(2024, 1, 1),
        )
        with pytest.raises(HTTPException) as exc:
            MedicationOrderService(db).create(9999, data)
        assert exc.value.status_code == 404

    def test_create_order_medication_not_found(self, db, make_admission):
        admission = make_admission()
        data = MedicationOrderCreate(
            admission_id=admission.id,
            medication_id=9999,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.prn,
            start_date=date(2024, 1, 1),
        )
        with pytest.raises(HTTPException) as exc:
            MedicationOrderService(db).create(admission.id, data)
        assert exc.value.status_code == 404

    def test_list_by_admission(self, db, make_admission, make_order):
        admission = make_admission()
        make_order(admission=admission)
        make_order(admission=admission)
        result = MedicationOrderService(db).list_by_admission(admission.id)
        assert len(result) == 2

    def test_list_by_admission_not_found(self, db):
        with pytest.raises(HTTPException) as exc:
            MedicationOrderService(db).list_by_admission(9999)
        assert exc.value.status_code == 404

    def test_patch_status(self, db, make_order):
        order = make_order()
        data = MedicationOrderPatch(status=OrderStatus.suspended)
        result = MedicationOrderService(db).patch(order.id, data)
        assert result.status == OrderStatus.suspended

    def test_patch_not_found(self, db):
        data = MedicationOrderPatch(status=OrderStatus.finished)
        with pytest.raises(HTTPException) as exc:
            MedicationOrderService(db).patch(9999, data)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Pase del día — generación lazy e idempotencia
# ---------------------------------------------------------------------------

class TestDailyPass:
    def _make_active_admission_with_order(self, db, make_admission, make_medication, make_slot):
        """Crea admisión activa, slot y orden scheduled con ese slot."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        slot = make_slot(time=time(8, 0))
        med = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=med.id,
            dose="1 tableta",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            times=[str(slot.id)],
            start_date=date(2024, 1, 1),
            status=OrderStatus.active,
            is_controlled=False,
        )
        db.add(order)
        db.commit()
        return admission, slot, order

    def test_lazy_generation_creates_pending(self, db, make_admission, make_medication, make_slot):
        self._make_active_admission_with_order(db, make_admission, make_medication, make_slot)
        target = date(2024, 6, 1)
        result = DailyPassService(db).get_pass(target)
        assert len(result.entries) == 1
        assert result.entries[0].status == AdministrationStatus.pending

    def test_lazy_generation_idempotent(self, db, make_admission, make_medication, make_slot):
        """Llamar el pase dos veces NO duplica administraciones."""
        self._make_active_admission_with_order(db, make_admission, make_medication, make_slot)
        target = date(2024, 6, 1)
        DailyPassService(db).get_pass(target)
        DailyPassService(db).get_pass(target)
        count = db.query(MedicationAdministration).count()
        assert count == 1

    def test_pass_excludes_inactive_admissions(
        self, db, make_admission, make_medication, make_slot
    ):
        """Admisiones discharged no aparecen en el pase."""
        admission = make_admission(status=AdmissionStatus.discharged)
        slot = make_slot(time=time(8, 0))
        med = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=med.id,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            times=[str(slot.id)],
            start_date=date(2024, 1, 1),
            status=OrderStatus.active,
            is_controlled=False,
        )
        db.add(order)
        db.commit()
        result = DailyPassService(db).get_pass(date(2024, 6, 1))
        assert len(result.entries) == 0

    def test_pass_excludes_order_outside_date_range(
        self, db, make_admission, make_medication, make_slot
    ):
        """Orden con end_date < target_date no genera toma."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        slot = make_slot(time=time(8, 0))
        med = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=med.id,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            times=[str(slot.id)],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 5, 31),  # vence antes de target
            status=OrderStatus.active,
            is_controlled=False,
        )
        db.add(order)
        db.commit()
        result = DailyPassService(db).get_pass(date(2024, 6, 1))
        assert len(result.entries) == 0

    def test_is_overdue_flag(self, db, make_admission, make_medication):
        """Una toma pending con scheduled_at pasado + margen marca is_overdue."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        med = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=med.id,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            times=[],
            start_date=date(2020, 1, 1),
            status=OrderStatus.active,
            is_controlled=False,
        )
        db.add(order)
        db.flush()

        # Toma scheduled_at hace 2 horas (muy pasada del margen de 60 min)
        past_time = datetime.now(timezone.utc) - timedelta(hours=2)
        adm_row = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=past_time,
            status=AdministrationStatus.pending,
        )
        db.add(adm_row)
        db.commit()

        # Llamar al pase para la fecha de la toma vencida
        target = past_time.date()
        result = DailyPassService(db).get_pass(target)

        # Buscar la entrada de esa toma
        entry = next((e for e in result.entries if e.administration_id == adm_row.id), None)
        assert entry is not None
        assert entry.is_overdue is True

    def test_not_overdue_when_within_margin(self, db, make_admission, make_medication):
        """Toma pending cuyo scheduled_at aún está dentro del margen NO es overdue."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        med = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=med.id,
            dose="1",
            route="oral",
            schedule_type=ScheduleType.scheduled,
            times=[],
            start_date=date(2020, 1, 1),
            status=OrderStatus.active,
            is_controlled=False,
        )
        db.add(order)
        db.flush()

        # Toma scheduled 10 minutos en el futuro (dentro del margen de 60 min)
        future_time = datetime.now(timezone.utc) + timedelta(minutes=10)
        adm_row = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=future_time,
            status=AdministrationStatus.pending,
        )
        db.add(adm_row)
        db.commit()

        target = future_time.date()
        result = DailyPassService(db).get_pass(target)
        entry = next((e for e in result.entries if e.administration_id == adm_row.id), None)
        assert entry is not None
        assert entry.is_overdue is False


# ---------------------------------------------------------------------------
# Record de tomas
# ---------------------------------------------------------------------------

class TestAdministrationRecord:
    USER_ID = 1

    def test_record_taken_ok(self, db, make_administration):
        adm = make_administration()
        data = AdministrationRecord(status=AdministrationStatus.taken)
        result = AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert result.status == AdministrationStatus.taken
        assert result.administered_by_user_id == self.USER_ID
        assert result.administered_at is not None

    def test_record_refused_without_reason_raises_400(self, db, make_administration):
        adm = make_administration()
        data = AdministrationRecord(status=AdministrationStatus.refused)
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert exc.value.status_code == 400

    def test_record_omitted_without_reason_raises_400(self, db, make_administration):
        adm = make_administration()
        data = AdministrationRecord(status=AdministrationStatus.omitted)
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert exc.value.status_code == 400

    def test_record_refused_with_reason_ok(self, db, make_administration):
        adm = make_administration()
        data = AdministrationRecord(status=AdministrationStatus.refused, reason="El paciente se negó")
        result = AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert result.status == AdministrationStatus.refused

    def test_record_controlled_without_witness_raises_400(self, db, make_order, make_administration):
        order = make_order(is_controlled=True)
        adm = make_administration(order=order)
        data = AdministrationRecord(status=AdministrationStatus.taken)
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert exc.value.status_code == 400

    def test_record_controlled_with_witness_ok(self, db, make_order, make_administration):
        order = make_order(is_controlled=True)
        adm = make_administration(order=order)
        data = AdministrationRecord(status=AdministrationStatus.taken, witness_user_id=2)
        result = AdministrationService(db).record(adm.id, data, self.USER_ID)
        assert result.status == AdministrationStatus.taken
        assert result.witness_user_id == 2

    def test_record_not_found_raises_404(self, db):
        data = AdministrationRecord(status=AdministrationStatus.taken)
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record(9999, data, self.USER_ID)
        assert exc.value.status_code == 404

    def test_record_sets_administered_at_default(self, db, make_administration):
        adm = make_administration()
        before = datetime.now(timezone.utc)
        data = AdministrationRecord(status=AdministrationStatus.taken)
        result = AdministrationService(db).record(adm.id, data, self.USER_ID)
        after = datetime.now(timezone.utc)
        # administered_at debe estar entre before y after
        assert result.administered_at is not None
        # Comparar con timezone
        adm_at = result.administered_at
        if adm_at.tzinfo is None:
            adm_at = adm_at.replace(tzinfo=timezone.utc)
        assert before <= adm_at <= after


# ---------------------------------------------------------------------------
# PRN
# ---------------------------------------------------------------------------

class TestPRN:
    USER_ID = 1

    def test_prn_with_reason_ok(self, db, make_admission, make_medication, make_order):
        admission = make_admission()
        order = make_order(admission=admission)
        data = PRNRecord(reason="Dolor agudo")
        result = AdministrationService(db).record_prn(admission.id, order.id, data, self.USER_ID)
        assert result.status == AdministrationStatus.taken
        assert result.reason == "Dolor agudo"
        assert result.scheduled_at is None
        assert result.administered_by_user_id == self.USER_ID

    def test_prn_order_not_found_raises_404(self, db, make_admission):
        admission = make_admission()
        data = PRNRecord(reason="Motivo")
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record_prn(admission.id, 9999, data, self.USER_ID)
        assert exc.value.status_code == 404

    def test_prn_wrong_admission_raises_404(self, db, make_admission, make_order):
        admission1 = make_admission()
        admission2 = make_admission()
        order = make_order(admission=admission1)
        data = PRNRecord(reason="Motivo")
        with pytest.raises(HTTPException) as exc:
            AdministrationService(db).record_prn(admission2.id, order.id, data, self.USER_ID)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Alergias
# ---------------------------------------------------------------------------

class TestAllergies:
    def test_create_and_list(self, db, make_resident):
        resident = make_resident()
        data = ResidentAllergyCreate(
            resident_id=resident.id,
            substance="Penicilina",
            reaction="Urticaria",
            severity="severe",
        )
        created = ResidentAllergyService(db).create(resident.id, data)
        assert created.id is not None
        assert created.substance == "Penicilina"

        listed = ResidentAllergyService(db).list(resident.id)
        assert len(listed) == 1
        assert listed[0].substance == "Penicilina"

    def test_list_resident_not_found(self, db):
        with pytest.raises(HTTPException) as exc:
            ResidentAllergyService(db).list(9999)
        assert exc.value.status_code == 404

    def test_create_resident_not_found(self, db):
        data = ResidentAllergyCreate(resident_id=9999, substance="Algo")
        with pytest.raises(HTTPException) as exc:
            ResidentAllergyService(db).create(9999, data)
        assert exc.value.status_code == 404

    def test_delete(self, db, make_resident):
        resident = make_resident()
        data = ResidentAllergyCreate(resident_id=resident.id, substance="Látex")
        created = ResidentAllergyService(db).create(resident.id, data)

        ResidentAllergyService(db).delete(resident.id, created.id)

        listed = ResidentAllergyService(db).list(resident.id)
        assert len(listed) == 0

    def test_delete_not_found(self, db, make_resident):
        resident = make_resident()
        with pytest.raises(HTTPException) as exc:
            ResidentAllergyService(db).delete(resident.id, 9999)
        assert exc.value.status_code == 404

    def test_delete_wrong_resident(self, db, make_resident):
        r1 = make_resident()
        r2 = make_resident()
        data = ResidentAllergyCreate(resident_id=r1.id, substance="Polen")
        created = ResidentAllergyService(db).create(r1.id, data)
        with pytest.raises(HTTPException) as exc:
            ResidentAllergyService(db).delete(r2.id, created.id)
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Franjas horarias
# ---------------------------------------------------------------------------

class TestMedTimeSlots:
    def test_list_empty(self, db):
        result = MedTimeSlotsService(db).list()
        assert result == []

    def test_put_creates_slots(self, db):
        slots_in = [
            MedTimeSlotUpdate(label="Mañana", time=time(6, 0), sort_order=1),
            MedTimeSlotUpdate(label="Noche", time=time(21, 0), sort_order=2),
        ]
        result = MedTimeSlotsService(db).put(slots_in)
        assert len(result) == 2
        labels = [s.label for s in result]
        assert "Mañana" in labels
        assert "Noche" in labels

    def test_put_idempotent_update(self, db):
        """PUT con id existente actualiza, no duplica."""
        slots_in = [MedTimeSlotUpdate(label="Mañana", time=time(6, 0), sort_order=1)]
        created = MedTimeSlotsService(db).put(slots_in)
        slot_id = created[0].id

        updated = MedTimeSlotsService(db).put(
            [MedTimeSlotUpdate(id=slot_id, label="Mañana Temprano", time=time(5, 30), sort_order=1)]
        )
        assert len(updated) == 1
        assert updated[0].label == "Mañana Temprano"
        assert updated[0].id == slot_id

    def test_put_removes_omitted_slots(self, db):
        """Franjas no incluidas en PUT se eliminan."""
        slots_in = [
            MedTimeSlotUpdate(label="A", time=time(6, 0), sort_order=1),
            MedTimeSlotUpdate(label="B", time=time(12, 0), sort_order=2),
        ]
        created = MedTimeSlotsService(db).put(slots_in)
        id_a = next(s.id for s in created if s.label == "A")

        # Solo mantenemos A
        result = MedTimeSlotsService(db).put(
            [MedTimeSlotUpdate(id=id_a, label="A", time=time(6, 0), sort_order=1)]
        )
        assert len(result) == 1
        assert result[0].label == "A"

    def test_get_returns_existing_slots(self, db, make_slot):
        make_slot(label="Tarde", time=time(18, 0))
        result = MedTimeSlotsService(db).list()
        assert any(s.label == "Tarde" for s in result)
