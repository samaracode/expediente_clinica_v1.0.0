"""
Tests para los 3 gaps cerrados en la Fase 1 del módulo de Medicamentos (MAR).

Gap 1 — Historial de tomas por orden: GET /medication-orders/{order_id}/administrations
Gap 2 — Notificaciones de dosis omitidas (overdue_medication en NotificationService)
Gap 3 — Alergias del residente incluidas en el pase del día (PassEntryOut.allergies)
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
    ResidentAllergy,
    ScheduleType,
)
from app.models.admission import AdmissionStatus
from app.services.medication_service import (
    DailyPassService,
    MedicationOrderService,
)
from app.services.notification_service import NotificationService


# ---------------------------------------------------------------------------
# Fixtures auxiliares locales
# ---------------------------------------------------------------------------

@pytest.fixture
def make_medication(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {"name": f"Med {counter['n']}", "is_controlled": False}
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
# Gap 1 — Historial de tomas por orden
# ---------------------------------------------------------------------------

class TestOrderAdministrationHistory:
    def test_returns_administrations_for_order(self, db, make_order, make_administration):
        order = make_order()
        t1 = datetime.now(timezone.utc) - timedelta(hours=3)
        t2 = datetime.now(timezone.utc) - timedelta(hours=1)
        adm1 = make_administration(order=order, scheduled_at=t1)
        adm2 = make_administration(order=order, scheduled_at=t2, status=AdministrationStatus.taken)
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order.id)

        assert len(result) == 2
        ids = {r.id for r in result}
        assert adm1.id in ids
        assert adm2.id in ids

    def test_returns_most_recent_first(self, db, make_order, make_administration):
        order = make_order()
        t_old = datetime.now(timezone.utc) - timedelta(hours=5)
        t_new = datetime.now(timezone.utc) - timedelta(hours=1)
        adm_old = make_administration(order=order, scheduled_at=t_old)
        adm_new = make_administration(order=order, scheduled_at=t_new)
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order.id)

        # más reciente primero
        assert result[0].id == adm_new.id
        assert result[1].id == adm_old.id

    def test_only_returns_administrations_of_requested_order(self, db, make_order, make_administration):
        order_a = make_order()
        order_b = make_order()
        adm_a = make_administration(order=order_a)
        make_administration(order=order_b)
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order_a.id)

        assert len(result) == 1
        assert result[0].id == adm_a.id

    def test_returns_empty_list_when_no_administrations(self, db, make_order):
        order = make_order()
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order.id)

        assert result == []

    def test_raises_404_if_order_not_found(self, db):
        with pytest.raises(HTTPException) as exc:
            MedicationOrderService(db).list_administrations_by_order(9999)
        assert exc.value.status_code == 404

    def test_is_overdue_flag_set_on_overdue_pending(self, db, make_order, make_administration):
        order = make_order()
        past = datetime.now(timezone.utc) - timedelta(hours=3)  # >60 min atrás
        make_administration(order=order, scheduled_at=past, status=AdministrationStatus.pending)
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order.id)

        assert result[0].is_overdue is True

    def test_is_overdue_false_for_taken(self, db, make_order, make_administration):
        order = make_order()
        past = datetime.now(timezone.utc) - timedelta(hours=3)
        make_administration(order=order, scheduled_at=past, status=AdministrationStatus.taken)
        db.commit()

        result = MedicationOrderService(db).list_administrations_by_order(order.id)

        assert result[0].is_overdue is False


# ---------------------------------------------------------------------------
# Gap 2 — Notificaciones de dosis omitidas
# ---------------------------------------------------------------------------

class TestOverdueMedicationNotification:
    def _make_pending_adm_at(self, db, make_admission, make_medication, make_order, scheduled_at):
        """Helper: crea una toma pending con scheduled_at dado."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        order = make_order(admission=admission)
        adm = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=scheduled_at,
            status=AdministrationStatus.pending,
        )
        db.add(adm)
        db.commit()
        return adm

    def test_overdue_medication_included_when_past_margin(
        self, db, make_admission, make_medication, make_order
    ):
        # scheduled_at hace 2 horas → vencida (margen default 60 min)
        past = datetime.now(timezone.utc) - timedelta(hours=2)
        self._make_pending_adm_at(db, make_admission, make_medication, make_order, past)

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 1
        assert "Dosis vencida:" in overdue[0].message

    def test_overdue_medication_excludes_inactive_admissions(
        self, db, make_admission, make_medication, make_order
    ):
        # Dosis vencida de un residente EGRESADO no debe notificar;
        # la de un residente activo sí.
        past = datetime.now(timezone.utc) - timedelta(hours=2)

        discharged = make_admission(status=AdmissionStatus.discharged)
        d_order = make_order(admission=discharged)
        db.add(MedicationAdministration(
            order_id=d_order.id, admission_id=discharged.id,
            scheduled_at=past, status=AdministrationStatus.pending,
        ))

        active = make_admission(status=AdmissionStatus.treatment_active)
        a_order = make_order(admission=active)
        db.add(MedicationAdministration(
            order_id=a_order.id, admission_id=active.id,
            scheduled_at=past, status=AdministrationStatus.pending,
        ))
        db.commit()

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 1
        assert overdue[0].entity_id == active.id

    def test_overdue_medication_not_included_within_margin(
        self, db, make_admission, make_medication, make_order
    ):
        # scheduled_at hace 30 min → aún dentro del margen de 60 min
        recent = datetime.now(timezone.utc) - timedelta(minutes=30)
        self._make_pending_adm_at(db, make_admission, make_medication, make_order, recent)

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 0

    def test_overdue_medication_not_included_when_taken(
        self, db, make_admission, make_medication, make_order
    ):
        # toma tomada (status=taken) aunque scheduled_at esté muy atrás
        past = datetime.now(timezone.utc) - timedelta(hours=5)
        admission = make_admission(status=AdmissionStatus.treatment_active)
        order = make_order(admission=admission)
        adm = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=past,
            status=AdministrationStatus.taken,
        )
        db.add(adm)
        db.commit()

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 0

    def test_overdue_medication_not_included_when_omitted(
        self, db, make_admission, make_medication, make_order
    ):
        past = datetime.now(timezone.utc) - timedelta(hours=5)
        admission = make_admission(status=AdmissionStatus.treatment_active)
        order = make_order(admission=admission)
        adm = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=past,
            status=AdministrationStatus.omitted,
        )
        db.add(adm)
        db.commit()

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 0

    def test_overdue_notification_message_contains_medication_name_and_resident(
        self, db, make_admission, make_medication, make_order, make_resident
    ):
        resident = make_resident(first_name="Ana", last_name="García")
        admission = make_admission(resident=resident, status=AdmissionStatus.treatment_active)
        medication = make_medication(name="Diazepam")
        order = make_order(admission=admission, medication=medication)
        past = datetime.now(timezone.utc) - timedelta(hours=3)
        adm = MedicationAdministration(
            order_id=order.id,
            admission_id=admission.id,
            scheduled_at=past,
            status=AdministrationStatus.pending,
        )
        db.add(adm)
        db.commit()

        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]

        assert len(overdue) == 1
        assert "Diazepam" in overdue[0].message
        assert "Ana García" in overdue[0].message
        assert overdue[0].entity_id == admission.id
        assert overdue[0].entity_type == "medication_administration"

    def test_no_overdue_notifications_when_no_pending(self, db):
        notifications = NotificationService(db).get_notifications()
        overdue = [n for n in notifications if n.type == "overdue_medication"]
        assert overdue == []


# ---------------------------------------------------------------------------
# Gap 3 — Alergias del residente en el pase del día
# ---------------------------------------------------------------------------

class TestPassEntryAllergies:
    def _setup_active_admission_with_order_and_slot(
        self, db, make_admission, make_medication, make_slot, resident=None
    ):
        """Crea la estructura mínima para que get_pass genere una entrada."""
        admission = make_admission(
            resident=resident,
            status=AdmissionStatus.treatment_active,
        )
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

    def test_pass_includes_allergies_for_resident(
        self, db, make_resident, make_admission, make_medication, make_slot
    ):
        resident = make_resident()
        allergy = ResidentAllergy(
            resident_id=resident.id,
            substance="Penicilina",
            severity="severe",
        )
        db.add(allergy)
        db.flush()

        self._setup_active_admission_with_order_and_slot(
            db, make_admission, make_medication, make_slot, resident=resident
        )

        result = DailyPassService(db).get_pass(date(2024, 6, 1))

        assert len(result.entries) == 1
        entry = result.entries[0]
        assert len(entry.allergies) == 1
        assert entry.allergies[0].substance == "Penicilina"
        assert entry.allergies[0].severity.value == "severe"

    def test_pass_empty_allergies_when_none_registered(
        self, db, make_admission, make_medication, make_slot
    ):
        self._setup_active_admission_with_order_and_slot(
            db, make_admission, make_medication, make_slot
        )

        result = DailyPassService(db).get_pass(date(2024, 6, 1))

        assert len(result.entries) == 1
        assert result.entries[0].allergies == []

    def test_pass_multiple_allergies(
        self, db, make_resident, make_admission, make_medication, make_slot
    ):
        resident = make_resident()
        for substance in ["Penicilina", "Látex", "Polen"]:
            db.add(ResidentAllergy(resident_id=resident.id, substance=substance))
        db.flush()

        self._setup_active_admission_with_order_and_slot(
            db, make_admission, make_medication, make_slot, resident=resident
        )

        result = DailyPassService(db).get_pass(date(2024, 6, 1))

        assert len(result.entries[0].allergies) == 3

    def test_pass_allergies_no_n_plus_1_with_multiple_residents(
        self, db, make_resident, make_admission, make_medication, make_slot
    ):
        """Dos residentes con alergias distintas, el pase devuelve las de cada uno."""
        r1 = make_resident()
        r2 = make_resident()
        db.add(ResidentAllergy(resident_id=r1.id, substance="Látex"))
        db.add(ResidentAllergy(resident_id=r2.id, substance="Polen"))
        db.flush()

        # Ambos tienen una orden activa en el mismo slot
        slot = make_slot(time=time(8, 0))
        med = make_medication()

        for resident in (r1, r2):
            admission = make_admission(resident=resident, status=AdmissionStatus.treatment_active)
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

        result = DailyPassService(db).get_pass(date(2024, 6, 1))

        assert len(result.entries) == 2
        # Cada entry debe tener exactamente 1 alergia (la de su propio residente)
        for entry in result.entries:
            assert len(entry.allergies) == 1
