"""
Tests para el módulo de Entrega de turno (Shift Handover) — Fase 4.

Nivel servicio (usando el fixture `db` en SQLite), consistente con el resto de
la suite (sin TestClient/httpx). Cubren:
- auto-resumen: dosis omitidas/rechazadas de la ventana, ausencias del roll-call,
  permisos del día, ingresos del día
- get_or_create del handover (open)
- close (congela auto_summary, setea closed_by/closed_at/status) y 400 si ya cerrado
- receive (400 si no está closed; OK si está closed)
- incidentes (crear / listar / 404)
- tareas (crear / listar / 404) y patch (marcar done + done_by, editar, 404)
"""

import pytest
from datetime import date, datetime, timezone, timedelta

from fastapi import HTTPException

from app.models.attendance import AttendanceRollCall, AttendanceEntry, PresenceStatus, Shift
from app.models.admission import AdmissionStatus
from app.models.follow_up import ExitPass, PassStatus, PassType
from app.models.medication import (
    Medication,
    MedicationOrder,
    MedicationAdministration,
    AdministrationStatus,
    MedicationRoute,
    ScheduleType,
)
from app.models.handover import HandoverStatus, IncidentSeverity
from app.schemas.handover import (
    ShiftIncidentCreate,
    ShiftTaskCreate,
    ShiftTaskPatch,
)
from app.services.handover_service import HandoverService


TARGET_DATE = date(2025, 3, 15)
MORNING_START = datetime(2025, 3, 15, 7, 0, tzinfo=timezone.utc)
AFTERNOON_START = datetime(2025, 3, 15, 15, 0, tzinfo=timezone.utc)
OUTSIDE_WINDOW = datetime(2025, 3, 15, 5, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Fixtures locales
# ---------------------------------------------------------------------------

@pytest.fixture
def make_medication(db):
    counter = {"n": 0}

    def _make(**kwargs):
        counter["n"] += 1
        defaults = {"name": f"Medicamento {counter['n']}", "is_controlled": False}
        defaults.update(kwargs)
        m = Medication(**defaults)
        db.add(m)
        db.flush()
        return m

    return _make


@pytest.fixture
def make_administration(db, make_medication):
    counter = {"n": 0}

    def _make(admission, **kwargs):
        counter["n"] += 1
        medication = make_medication()
        order = MedicationOrder(
            admission_id=admission.id,
            medication_id=medication.id,
            dose="10mg",
            route=MedicationRoute.oral,
            schedule_type=ScheduleType.scheduled,
            start_date=date(2025, 1, 1),
        )
        db.add(order)
        db.flush()
        defaults = {
            "order_id": order.id,
            "admission_id": admission.id,
            "status": AdministrationStatus.pending,
            "scheduled_at": MORNING_START,
        }
        defaults.update(kwargs)
        a = MedicationAdministration(**defaults)
        db.add(a)
        db.flush()
        return a

    return _make


@pytest.fixture
def make_roll_call(db):
    def _make(target_date, shift, **kwargs):
        rc = AttendanceRollCall(date=target_date, shift=shift, **kwargs)
        db.add(rc)
        db.flush()
        return rc

    return _make


@pytest.fixture
def make_attendance_entry(db):
    def _make(roll_call, admission, expected, actual, note=None):
        entry = AttendanceEntry(
            roll_call_id=roll_call.id,
            admission_id=admission.id,
            expected_status=expected,
            actual_status=actual,
            note=note,
        )
        db.add(entry)
        db.flush()
        return entry

    return _make


@pytest.fixture
def make_exit_pass(db):
    def _make(admission, **kwargs):
        defaults = {
            "admission_id": admission.id,
            "status": PassStatus.approved,
            "pass_type": PassType.regular,
            "departure_date": datetime(2025, 3, 15, 9, 0, tzinfo=timezone.utc),
            "return_date_actual": None,
        }
        defaults.update(kwargs)
        ep = ExitPass(**defaults)
        db.add(ep)
        db.flush()
        return ep

    return _make


# ---------------------------------------------------------------------------
# Auto-resumen: medicamentos
# ---------------------------------------------------------------------------

class TestAutoSummaryMedications:
    def test_omitted_in_window_included(self, db, make_admission, make_administration):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_administration(admission, status=AdministrationStatus.omitted, scheduled_at=MORNING_START)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["medications"]) == 1
        assert summary["medications"][0]["status"] == "omitted"

    def test_refused_in_window_included(self, db, make_admission, make_administration):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_administration(admission, status=AdministrationStatus.refused, scheduled_at=MORNING_START)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["medications"]) == 1
        assert summary["medications"][0]["status"] == "refused"

    def test_taken_not_included(self, db, make_admission, make_administration):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_administration(admission, status=AdministrationStatus.taken, scheduled_at=MORNING_START)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["medications"]) == 0

    def test_outside_window_not_included(self, db, make_admission, make_administration):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_administration(admission, status=AdministrationStatus.omitted, scheduled_at=OUTSIDE_WINDOW)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["medications"]) == 0

    def test_afternoon_window_separate(self, db, make_admission, make_administration):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_administration(admission, status=AdministrationStatus.omitted, scheduled_at=AFTERNOON_START)
        db.commit()
        svc = HandoverService(db)
        assert len(svc.compute_auto_summary(TARGET_DATE, Shift.morning)["medications"]) == 0
        assert len(svc.compute_auto_summary(TARGET_DATE, Shift.afternoon)["medications"]) == 1


# ---------------------------------------------------------------------------
# Auto-resumen: asistencia
# ---------------------------------------------------------------------------

class TestAutoSummaryAttendance:
    def test_awol_included(self, db, make_admission, make_roll_call, make_attendance_entry):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        rc = make_roll_call(TARGET_DATE, Shift.morning)
        make_attendance_entry(rc, admission, PresenceStatus.present, PresenceStatus.absent_without_leave, "No estaba")
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["attendance"]) == 1
        assert summary["attendance"][0]["actual_status"] == "absent_without_leave"

    def test_discrepancy_included(self, db, make_admission, make_roll_call, make_attendance_entry):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        rc = make_roll_call(TARGET_DATE, Shift.morning)
        make_attendance_entry(rc, admission, PresenceStatus.present, PresenceStatus.on_pass)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["attendance"]) == 1

    def test_matching_not_included(self, db, make_admission, make_roll_call, make_attendance_entry):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        rc = make_roll_call(TARGET_DATE, Shift.morning)
        make_attendance_entry(rc, admission, PresenceStatus.present, PresenceStatus.present)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["attendance"]) == 0

    def test_no_roll_call_empty(self, db, make_admission):
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["attendance"]) == 0


# ---------------------------------------------------------------------------
# Auto-resumen: permisos e ingresos
# ---------------------------------------------------------------------------

class TestAutoSummaryPassesAndAdmissions:
    def test_departure_today_included(self, db, make_admission, make_exit_pass):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_exit_pass(admission, departure_date=datetime(2025, 3, 15, 9, 0, tzinfo=timezone.utc))
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["exit_passes"]) == 1
        assert "departure" in summary["exit_passes"][0]["events"]

    def test_return_today_included(self, db, make_admission, make_exit_pass):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_exit_pass(
            admission,
            departure_date=datetime(2025, 3, 14, 9, 0, tzinfo=timezone.utc),
            return_date_actual=datetime(2025, 3, 15, 17, 0, tzinfo=timezone.utc),
        )
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["exit_passes"]) == 1
        assert "return" in summary["exit_passes"][0]["events"]

    def test_other_date_not_included(self, db, make_admission, make_exit_pass):
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()
        make_exit_pass(admission, departure_date=datetime(2025, 3, 10, 9, 0, tzinfo=timezone.utc))
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["exit_passes"]) == 0

    def test_admissions_today_included(self, db, make_admission):
        make_admission(status=AdmissionStatus.treatment_active, admission_date=TARGET_DATE)
        db.commit()
        summary = HandoverService(db).compute_auto_summary(TARGET_DATE, Shift.morning)
        assert len(summary["admissions"]) == 1


# ---------------------------------------------------------------------------
# Handover: get_or_create, close, receive
# ---------------------------------------------------------------------------

class TestHandoverLifecycle:
    def test_creates_open_handover(self, db):
        out = HandoverService(db).get_handover(TARGET_DATE, Shift.morning)
        assert out.status == HandoverStatus.open
        assert out.date == TARGET_DATE
        assert out.shift == Shift.morning

    def test_returns_existing(self, db):
        svc = HandoverService(db)
        o1 = svc.get_handover(TARGET_DATE, Shift.afternoon)
        o2 = svc.get_handover(TARGET_DATE, Shift.afternoon)
        assert o1.id == o2.id

    def test_auto_summary_included_when_open(self, db):
        out = HandoverService(db).get_handover(TARGET_DATE, Shift.night)
        assert out.auto_summary is not None

    def test_close_freezes_summary(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        closed = svc.close(h.id, user.id, None)
        assert closed.status == HandoverStatus.closed
        assert closed.closed_by_user_id == user.id
        assert closed.closed_at is not None
        assert closed.auto_summary is not None

    def test_close_already_closed_400(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        svc.close(h.id, user.id, None)
        with pytest.raises(HTTPException) as exc:
            svc.close(h.id, user.id, None)
        assert exc.value.status_code == 400

    def test_receive_open_400(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        with pytest.raises(HTTPException) as exc:
            svc.receive(h.id, user.id)
        assert exc.value.status_code == 400

    def test_receive_after_close(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        svc.close(h.id, user.id, None)
        received = svc.receive(h.id, user.id)
        assert received.status == HandoverStatus.received
        assert received.received_by_user_id == user.id
        assert received.received_at is not None


# ---------------------------------------------------------------------------
# Incidentes
# ---------------------------------------------------------------------------

class TestIncidents:
    def test_list_empty(self, db):
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        assert svc.list_incidents(h.id) == []

    def test_create_and_list(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        created = svc.create_incident(
            h.id,
            ShiftIncidentCreate(type="conducta", severity=IncidentSeverity.high, description="Residente alterado", action_taken="Contención verbal"),
            user.id,
        )
        assert created.type == "conducta"
        assert created.severity == IncidentSeverity.high
        assert created.reported_by_user_id == user.id
        assert len(svc.list_incidents(h.id)) == 1

    def test_create_404_handover(self, db, make_user):
        user = make_user()
        db.commit()
        with pytest.raises(HTTPException) as exc:
            HandoverService(db).create_incident(
                99999,
                ShiftIncidentCreate(type="x", severity=IncidentSeverity.low, description="t"),
                user.id,
            )
        assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# Tareas
# ---------------------------------------------------------------------------

class TestTasks:
    def test_list_empty(self, db):
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        assert svc.list_tasks(h.id) == []

    def test_create_and_list(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        created = svc.create_task(h.id, ShiftTaskCreate(description="Verificar medicamentos"), user.id)
        assert created.description == "Verificar medicamentos"
        assert created.is_done is False
        assert len(svc.list_tasks(h.id)) == 1

    def test_create_404_handover(self, db, make_user):
        user = make_user()
        db.commit()
        with pytest.raises(HTTPException) as exc:
            HandoverService(db).create_task(99999, ShiftTaskCreate(description="t"), user.id)
        assert exc.value.status_code == 404

    def test_patch_mark_done(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        task = svc.create_task(h.id, ShiftTaskCreate(description="Completar reporte"), user.id)
        patched = svc.patch_task(task.id, ShiftTaskPatch(is_done=True), user.id)
        assert patched.is_done is True
        assert patched.done_by_user_id == user.id

    def test_patch_edit_description(self, db, make_user):
        user = make_user()
        db.commit()
        svc = HandoverService(db)
        h = svc.get_handover(TARGET_DATE, Shift.morning)
        task = svc.create_task(h.id, ShiftTaskCreate(description="Original"), user.id)
        patched = svc.patch_task(task.id, ShiftTaskPatch(description="Actualizada"), user.id)
        assert patched.description == "Actualizada"

    def test_patch_404(self, db, make_user):
        user = make_user()
        db.commit()
        with pytest.raises(HTTPException) as exc:
            HandoverService(db).patch_task(99999, ShiftTaskPatch(is_done=True), user.id)
        assert exc.value.status_code == 404
