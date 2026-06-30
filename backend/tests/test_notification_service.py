from datetime import date, datetime, timedelta, timezone

import pytest

from app.models.follow_up import Consultation, ExitPass, PassStatus, PassType
from app.models.treatment import TreatmentPlan, TreatmentStage, StageName, StageStatus
from app.services.notification_service import NotificationService


def test_no_notifications_returns_empty(db):
    result = NotificationService(db).get_notifications()
    assert result == []


def test_upcoming_appointment_today(db, make_admission):
    a = make_admission()
    today = date.today()
    c = Consultation(admission_id=a.id, consultation_date=today, next_appointment_date=today)
    db.add(c)
    db.flush()
    result = NotificationService(db).get_notifications()
    appt_notifs = [n for n in result if n.type == "upcoming_appointment"]
    assert len(appt_notifs) == 1
    assert "hoy" in appt_notifs[0].message


def test_upcoming_appointment_tomorrow(db, make_admission):
    a = make_admission()
    tomorrow = date.today() + timedelta(days=1)
    c = Consultation(
        admission_id=a.id,
        consultation_date=date.today(),
        next_appointment_date=tomorrow,
    )
    db.add(c)
    db.flush()
    result = NotificationService(db).get_notifications()
    appt_notifs = [n for n in result if n.type == "upcoming_appointment"]
    assert any("mañana" in n.message for n in appt_notifs)


def test_upcoming_appointment_in_3_days(db, make_admission):
    a = make_admission()
    in_3 = date.today() + timedelta(days=3)
    c = Consultation(
        admission_id=a.id,
        consultation_date=date.today(),
        next_appointment_date=in_3,
    )
    db.add(c)
    db.flush()
    result = NotificationService(db).get_notifications()
    appt_notifs = [n for n in result if n.type == "upcoming_appointment"]
    assert len(appt_notifs) == 1


def test_appointment_beyond_3_days_not_included(db, make_admission):
    a = make_admission()
    in_4 = date.today() + timedelta(days=4)
    c = Consultation(
        admission_id=a.id,
        consultation_date=date.today(),
        next_appointment_date=in_4,
    )
    db.add(c)
    db.flush()
    result = NotificationService(db).get_notifications()
    appt_notifs = [n for n in result if n.type == "upcoming_appointment"]
    assert len(appt_notifs) == 0


def test_deleted_consultation_not_included(db, make_admission):
    a = make_admission()
    today = date.today()
    c = Consultation(
        admission_id=a.id,
        consultation_date=today,
        next_appointment_date=today,
        is_deleted=True,
    )
    db.add(c)
    db.flush()
    result = NotificationService(db).get_notifications()
    assert all(n.type != "upcoming_appointment" for n in result)


def test_overdue_exit_pass_notification(db, make_admission):
    a = make_admission()
    yesterday = datetime.now(timezone.utc) - timedelta(days=2)
    ep = ExitPass(
        admission_id=a.id,
        status=PassStatus.approved,
        return_date_expected=yesterday,
        return_date_actual=None,
        pass_type=PassType.regular,
    )
    db.add(ep)
    db.flush()
    result = NotificationService(db).get_notifications()
    overdue = [n for n in result if n.type == "overdue_exit_pass"]
    assert len(overdue) == 1
    assert "vencido" in overdue[0].message


def test_completed_exit_pass_not_overdue(db, make_admission):
    a = make_admission()
    yesterday = datetime.now(timezone.utc) - timedelta(days=2)
    now = datetime.now(timezone.utc)
    ep = ExitPass(
        admission_id=a.id,
        status=PassStatus.approved,
        return_date_expected=yesterday,
        return_date_actual=now,  # actually returned
        pass_type=PassType.regular,
    )
    db.add(ep)
    db.flush()
    result = NotificationService(db).get_notifications()
    overdue = [n for n in result if n.type == "overdue_exit_pass"]
    assert len(overdue) == 0


def test_upcoming_stage_end_notification(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    plan = TreatmentPlan(admission_id=a.id, created_by_id=user.id)
    db.add(plan)
    db.flush()
    in_5 = date.today() + timedelta(days=5)
    stage = TreatmentStage(
        treatment_plan_id=plan.id,
        stage_name=StageName.orientation,
        stage_order=1,
        status=StageStatus.active,
        end_date=in_5,
    )
    db.add(stage)
    db.flush()
    result = NotificationService(db).get_notifications()
    stage_notifs = [n for n in result if n.type == "upcoming_stage_end"]
    assert len(stage_notifs) == 1


def test_stage_end_beyond_7_days_not_included(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    plan = TreatmentPlan(admission_id=a.id, created_by_id=user.id)
    db.add(plan)
    db.flush()
    in_8 = date.today() + timedelta(days=8)
    stage = TreatmentStage(
        treatment_plan_id=plan.id,
        stage_name=StageName.orientation,
        stage_order=1,
        status=StageStatus.active,
        end_date=in_8,
    )
    db.add(stage)
    db.flush()
    result = NotificationService(db).get_notifications()
    stage_notifs = [n for n in result if n.type == "upcoming_stage_end"]
    assert len(stage_notifs) == 0


def test_results_sorted_by_due_date(db, make_admission):
    a1 = make_admission()
    a2 = make_admission()
    today = date.today()
    db.add(Consultation(
        admission_id=a1.id,
        consultation_date=today,
        next_appointment_date=today + timedelta(days=2),
    ))
    db.add(Consultation(
        admission_id=a2.id,
        consultation_date=today,
        next_appointment_date=today + timedelta(days=1),
    ))
    db.flush()
    result = NotificationService(db).get_notifications()
    dates = [n.due_date for n in result]
    assert dates == sorted(dates)
