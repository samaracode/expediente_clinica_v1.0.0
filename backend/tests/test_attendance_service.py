"""
Tests para el módulo de Asistencia — Fase 2.

Cubren:
- Roster pre-llenado: calcula `present` para activo sin permiso.
- Roster pre-llenado: calcula `on_pass` para activo con permiso vigente.
- POST persiste y luego GET devuelve lo guardado (con los estados confirmados).
- Upsert: un segundo POST para el mismo (date, shift) no duplica el roll-call.
- /attendance/today cuenta correctamente desde roll-call guardado.
- /attendance/today usa estado esperado si no hay roll-call.
- Notificación absent_without_leave aparece cuando corresponde.
- Historial por admisión devuelve entradas ordenadas.
- Admisión inactiva (discharged) no aparece en el roster esperado.
- Permiso expirado (return_date_expected anterior a la fecha) no cuenta como vigente.
"""

import pytest
from datetime import date, datetime, timedelta, timezone

from fastapi import HTTPException

from app.models.attendance import (
    AttendanceEntry,
    AttendanceRollCall,
    PresenceStatus,
    Shift,
)
from app.models.admission import AdmissionStatus
from app.models.follow_up import ExitPass, PassStatus, PassType
from app.schemas.attendance import EntryIn, RollCallCreate
from app.services.attendance_service import AttendanceService
from app.services.notification_service import NotificationService


# ---------------------------------------------------------------------------
# Fixtures auxiliares
# ---------------------------------------------------------------------------

@pytest.fixture
def make_exit_pass(db):
    """Crea un ExitPass para una admisión."""

    def _make(admission, **kwargs):
        defaults = {
            "admission_id": admission.id,
            "status": PassStatus.approved,
            "pass_type": PassType.regular,
            "departure_date": datetime(2024, 6, 1, 8, 0, tzinfo=timezone.utc),
            "return_date_expected": datetime(2024, 6, 3, 18, 0, tzinfo=timezone.utc),
            "return_date_actual": None,
        }
        defaults.update(kwargs)
        ep = ExitPass(**defaults)
        db.add(ep)
        db.flush()
        return ep

    return _make


TARGET_DATE = date(2024, 6, 2)  # dentro del rango del permiso de ejemplo


# ---------------------------------------------------------------------------
# Cálculo de expected_status
# ---------------------------------------------------------------------------

class TestExpectedStatus:
    def test_active_no_pass_is_present(self, db, make_admission):
        """Residente activo sin permiso → expected_status = present."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        entry = next((e for e in roster.entries if e.admission_id == admission.id), None)
        assert entry is not None
        assert entry.expected_status == PresenceStatus.present

    def test_active_with_valid_pass_is_on_pass(self, db, make_admission, make_exit_pass):
        """Residente activo con permiso vigente → expected_status = on_pass."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        make_exit_pass(
            admission,
            departure_date=datetime(2024, 6, 1, 8, 0, tzinfo=timezone.utc),
            return_date_expected=datetime(2024, 6, 3, 18, 0, tzinfo=timezone.utc),
        )
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        entry = next((e for e in roster.entries if e.admission_id == admission.id), None)
        assert entry is not None
        assert entry.expected_status == PresenceStatus.on_pass

    def test_expired_pass_not_on_pass(self, db, make_admission, make_exit_pass):
        """Permiso cuyo return_date_expected < fecha no cuenta como vigente → present."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        make_exit_pass(
            admission,
            departure_date=datetime(2024, 5, 28, 8, 0, tzinfo=timezone.utc),
            return_date_expected=datetime(2024, 5, 31, 18, 0, tzinfo=timezone.utc),  # ya venció
        )
        db.commit()

        svc = AttendanceService(db)
        # Verificar para TARGET_DATE = 2024-06-02 (posterior al vencimiento)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        entry = next((e for e in roster.entries if e.admission_id == admission.id), None)
        assert entry is not None
        assert entry.expected_status == PresenceStatus.present

    def test_pass_not_approved_not_counted(self, db, make_admission, make_exit_pass):
        """Permiso pendiente (no aprobado) no cuenta como vigente."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        make_exit_pass(
            admission,
            status=PassStatus.pending,
            departure_date=datetime(2024, 6, 1, 8, 0, tzinfo=timezone.utc),
            return_date_expected=datetime(2024, 6, 3, 18, 0, tzinfo=timezone.utc),
        )
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        entry = next((e for e in roster.entries if e.admission_id == admission.id), None)
        assert entry is not None
        assert entry.expected_status == PresenceStatus.present

    def test_inactive_admission_excluded(self, db, make_admission):
        """Admisión discharged no aparece en el roster esperado."""
        make_admission(status=AdmissionStatus.discharged)
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        # Solo el activo debería aparecer
        assert len(roster.entries) == 1

    def test_all_active_statuses_included(self, db, make_admission):
        """Los tres statuses activos (consents_pending, assessment, treatment) aparecen."""
        a1 = make_admission(status=AdmissionStatus.consents_pending)
        a2 = make_admission(status=AdmissionStatus.assessment_in_progress)
        a3 = make_admission(status=AdmissionStatus.treatment_active)
        make_admission(status=AdmissionStatus.intake_pending)  # NO debe aparecer
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(TARGET_DATE, Shift.morning)
        ids = {e.admission_id for e in roster.entries}
        assert a1.id in ids
        assert a2.id in ids
        assert a3.id in ids
        assert len(roster.entries) == 3


# ---------------------------------------------------------------------------
# POST (confirm) y GET (roster guardado)
# ---------------------------------------------------------------------------

class TestConfirmAndRetrieve:
    def test_post_persists_roll_call(self, db, make_admission, make_user):
        """POST crea un AttendanceRollCall con sus entries."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        data = RollCallCreate(
            date=TARGET_DATE,
            shift=Shift.morning,
            notes="Sin novedad",
            entries=[
                EntryIn(
                    admission_id=admission.id,
                    expected_status=PresenceStatus.present,
                    actual_status=PresenceStatus.present,
                )
            ],
        )
        svc = AttendanceService(db)
        result = svc.confirm_roll_call(data, current_user_id=user.id)

        assert result.id is not None
        assert result.shift == Shift.morning
        assert result.conducted_by_user_id == user.id
        assert len(result.entries) == 1
        assert result.entries[0].actual_status == PresenceStatus.present

    def test_get_returns_saved_roll_call(self, db, make_admission, make_user):
        """Después del POST, el GET devuelve los datos guardados (no calcula de nuevo)."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        data = RollCallCreate(
            date=TARGET_DATE,
            shift=Shift.afternoon,
            entries=[
                EntryIn(
                    admission_id=admission.id,
                    expected_status=PresenceStatus.present,
                    actual_status=PresenceStatus.absent_without_leave,
                    note="No se encontraba en su habitación",
                )
            ],
        )
        svc = AttendanceService(db)
        svc.confirm_roll_call(data, current_user_id=user.id)

        # Ahora GET debe devolver lo guardado
        roster = svc.get_roster(TARGET_DATE, Shift.afternoon)
        assert roster.roll_call_id is not None
        assert len(roster.entries) == 1
        entry = roster.entries[0]
        assert entry.actual_status == PresenceStatus.absent_without_leave
        assert entry.note == "No se encontraba en su habitación"
        assert entry.entry_id is not None

    def test_roster_no_roll_call_has_no_actual_status(self, db, make_admission):
        """GET sin roll-call guardado → actual_status = None en cada entrada."""
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = AttendanceService(db)
        roster = svc.get_roster(date(2099, 1, 1), Shift.night)
        assert roster.roll_call_id is None
        for entry in roster.entries:
            assert entry.actual_status is None


# ---------------------------------------------------------------------------
# Upsert
# ---------------------------------------------------------------------------

class TestUpsert:
    def test_second_post_updates_not_duplicates(self, db, make_admission, make_user):
        """Un segundo POST para (date, shift) actualiza el roll-call; no duplica."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        base_data = dict(date=TARGET_DATE, shift=Shift.morning, entries=[
            EntryIn(
                admission_id=admission.id,
                expected_status=PresenceStatus.present,
                actual_status=PresenceStatus.present,
            )
        ])

        svc.confirm_roll_call(RollCallCreate(**base_data), current_user_id=user.id)
        svc.confirm_roll_call(
            RollCallCreate(**{**base_data, "notes": "Actualizado"}),
            current_user_id=user.id,
        )

        # Solo debe haber 1 roll-call
        count = db.query(AttendanceRollCall).filter(
            AttendanceRollCall.date == TARGET_DATE,
            AttendanceRollCall.shift == Shift.morning,
        ).count()
        assert count == 1

        # Y las notes deben ser las del segundo POST
        rc = db.query(AttendanceRollCall).filter(
            AttendanceRollCall.date == TARGET_DATE,
            AttendanceRollCall.shift == Shift.morning,
        ).first()
        assert rc.notes == "Actualizado"

    def test_upsert_replaces_entries(self, db, make_admission, make_user):
        """El upsert reemplaza las entries previas (sin duplicar)."""
        a1 = make_admission(status=AdmissionStatus.treatment_active)
        a2 = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        # Primera confirmación con a1
        svc.confirm_roll_call(
            RollCallCreate(
                date=TARGET_DATE,
                shift=Shift.morning,
                entries=[
                    EntryIn(
                        admission_id=a1.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.present,
                    )
                ],
            ),
            current_user_id=user.id,
        )
        # Segunda confirmación con a1 y a2
        result = svc.confirm_roll_call(
            RollCallCreate(
                date=TARGET_DATE,
                shift=Shift.morning,
                entries=[
                    EntryIn(
                        admission_id=a1.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.on_pass,
                    ),
                    EntryIn(
                        admission_id=a2.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.present,
                    ),
                ],
            ),
            current_user_id=user.id,
        )
        assert len(result.entries) == 2
        # Total de entries en DB para este roll-call = 2 (no 3)
        rc = db.query(AttendanceRollCall).filter(
            AttendanceRollCall.date == TARGET_DATE,
            AttendanceRollCall.shift == Shift.morning,
        ).first()
        total_entries = db.query(AttendanceEntry).filter(
            AttendanceEntry.roll_call_id == rc.id
        ).count()
        assert total_entries == 2


# ---------------------------------------------------------------------------
# /attendance/today
# ---------------------------------------------------------------------------

class TestTodaySummary:
    def test_today_summary_from_roll_call(self, db, make_admission, make_user):
        """Con roll-call guardado, el resumen refleja los actual_status."""
        today = date.today()
        a1 = make_admission(status=AdmissionStatus.treatment_active)
        a2 = make_admission(status=AdmissionStatus.treatment_active)
        a3 = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        svc.confirm_roll_call(
            RollCallCreate(
                date=today,
                shift=Shift.morning,
                entries=[
                    EntryIn(
                        admission_id=a1.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.present,
                    ),
                    EntryIn(
                        admission_id=a2.id,
                        expected_status=PresenceStatus.on_pass,
                        actual_status=PresenceStatus.on_pass,
                    ),
                    EntryIn(
                        admission_id=a3.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.absent_without_leave,
                    ),
                ],
            ),
            current_user_id=user.id,
        )

        summary = svc.get_today_summary(today)
        assert summary.source == "roll_call"
        assert summary.total == 3
        assert summary.present == 1
        assert summary.on_pass == 1
        assert summary.absent_without_leave == 1
        assert summary.external_appointment == 0

    def test_today_summary_from_expected_when_no_roll_call(self, db, make_admission):
        """Sin roll-call, el resumen se calcula desde el estado esperado."""
        future_date = date(2099, 12, 31)
        make_admission(status=AdmissionStatus.treatment_active)
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        svc = AttendanceService(db)
        summary = svc.get_today_summary(future_date)
        assert summary.source == "expected"
        assert summary.total == 2
        assert summary.present == 2


# ---------------------------------------------------------------------------
# Historial por admisión
# ---------------------------------------------------------------------------

class TestAdmissionHistory:
    def test_history_returns_entries(self, db, make_admission, make_user):
        """GET /admissions/{id}/attendance devuelve entries del residente."""
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        for i, shift in enumerate([Shift.morning, Shift.afternoon]):
            svc.confirm_roll_call(
                RollCallCreate(
                    date=date(2024, 6, i + 1),
                    shift=shift,
                    entries=[
                        EntryIn(
                            admission_id=admission.id,
                            expected_status=PresenceStatus.present,
                            actual_status=PresenceStatus.present,
                        )
                    ],
                ),
                current_user_id=user.id,
            )

        history = svc.get_admission_history(admission.id)
        assert len(history) == 2
        for entry in history:
            assert entry.admission_id == admission.id

    def test_history_admission_not_found(self, db):
        """GET con admission_id inexistente → 404."""
        svc = AttendanceService(db)
        with pytest.raises(HTTPException) as exc:
            svc.get_admission_history(9999)
        assert exc.value.status_code == 404

    def test_history_empty_when_no_roll_calls(self, db, make_admission):
        """Admisión sin pases → lista vacía."""
        admission = make_admission()
        db.commit()
        svc = AttendanceService(db)
        result = svc.get_admission_history(admission.id)
        assert result == []


# ---------------------------------------------------------------------------
# Notificación absent_without_leave
# ---------------------------------------------------------------------------

class TestAbsentWithoutLeaveNotification:
    def test_notification_appears_when_awol(self, db, make_admission, make_user):
        """Si hay un entry AWOL en el último roll-call de hoy, aparece la notificación."""
        today = date.today()
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        svc.confirm_roll_call(
            RollCallCreate(
                date=today,
                shift=Shift.morning,
                entries=[
                    EntryIn(
                        admission_id=admission.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.absent_without_leave,
                    )
                ],
            ),
            current_user_id=user.id,
        )

        notifications = NotificationService(db).get_notifications()
        awol_notifs = [n for n in notifications if n.type == "absent_without_leave"]
        assert len(awol_notifs) == 1
        assert awol_notifs[0].entity_id == admission.id
        assert awol_notifs[0].entity_type == "attendance"
        assert "Ausente sin permiso" in awol_notifs[0].message

    def test_no_notification_when_present(self, db, make_admission, make_user):
        """Residente presente en el roll-call → sin notificación AWOL."""
        today = date.today()
        admission = make_admission(status=AdmissionStatus.treatment_active)
        user = make_user()
        db.commit()

        svc = AttendanceService(db)
        svc.confirm_roll_call(
            RollCallCreate(
                date=today,
                shift=Shift.morning,
                entries=[
                    EntryIn(
                        admission_id=admission.id,
                        expected_status=PresenceStatus.present,
                        actual_status=PresenceStatus.present,
                    )
                ],
            ),
            current_user_id=user.id,
        )

        notifications = NotificationService(db).get_notifications()
        awol_notifs = [n for n in notifications if n.type == "absent_without_leave"]
        assert len(awol_notifs) == 0

    def test_no_notification_when_no_roll_call_today(self, db, make_admission):
        """Sin roll-call hoy → sin notificación AWOL."""
        make_admission(status=AdmissionStatus.treatment_active)
        db.commit()

        notifications = NotificationService(db).get_notifications()
        awol_notifs = [n for n in notifications if n.type == "absent_without_leave"]
        assert len(awol_notifs) == 0
