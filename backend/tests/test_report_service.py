from datetime import date

import pytest

from app.models.admission import AdmissionStatus, AdmissionType
from app.models.follow_up import Consultation
from app.models.treatment import TreatmentPlan, TreatmentStage, StageName, StageStatus
from app.services.report_service import ReportService


def test_admissions_report_empty(db):
    result = ReportService(db).admissions_report()
    assert result == []


def test_admissions_report_returns_rows(db, make_admission, make_resident):
    r = make_resident(first_name="Luis", last_name="Vargas")
    make_admission(resident=r)
    result = ReportService(db).admissions_report()
    assert len(result) == 1
    assert result[0].resident_name == "Luis Vargas"


def test_admissions_report_includes_status(db, make_admission):
    make_admission(status=AdmissionStatus.discharged)
    result = ReportService(db).admissions_report()
    assert result[0].status == "discharged"


def test_admissions_report_includes_type(db, make_admission):
    make_admission()
    result = ReportService(db).admissions_report()
    assert result[0].admission_type in ("first", "readmission")


def test_admissions_report_limit_500(db, make_admission):
    for _ in range(5):
        make_admission()
    result = ReportService(db).admissions_report()
    assert len(result) == 5


def test_consultations_report_empty(db):
    result = ReportService(db).consultations_report()
    assert result == []


def test_consultations_report_returns_rows(db, make_admission, make_resident):
    r = make_resident(first_name="Ana", last_name="Cruz")
    a = make_admission(resident=r)
    c = Consultation(admission_id=a.id, consultation_date=date(2024, 5, 1))
    db.add(c)
    db.flush()
    result = ReportService(db).consultations_report()
    assert len(result) == 1
    assert result[0].resident_name == "Ana Cruz"


def test_consultations_report_no_professional_shows_dash(db, make_admission):
    a = make_admission()
    c = Consultation(admission_id=a.id, consultation_date=date(2024, 5, 1))
    db.add(c)
    db.flush()
    result = ReportService(db).consultations_report()
    assert result[0].professional_name == "—"


def test_treatment_progress_empty(db):
    result = ReportService(db).treatment_progress_report()
    assert result == []


def test_treatment_progress_returns_active_admissions(db, make_admission):
    make_admission(status=AdmissionStatus.treatment_active)
    make_admission(status=AdmissionStatus.assessment_in_progress)
    make_admission(status=AdmissionStatus.discharged)  # should not appear
    result = ReportService(db).treatment_progress_report()
    assert len(result) == 2


def test_treatment_progress_counts_completed_stages(db, make_admission, make_user):
    a = make_admission(status=AdmissionStatus.treatment_active)
    user = make_user()
    plan = TreatmentPlan(admission_id=a.id, created_by_id=user.id)
    db.add(plan)
    db.flush()
    db.add(TreatmentStage(
        treatment_plan_id=plan.id,
        stage_name=StageName.orientation,
        stage_order=1,
        status=StageStatus.completed,
    ))
    db.add(TreatmentStage(
        treatment_plan_id=plan.id,
        stage_name=StageName.adaptation,
        stage_order=2,
        status=StageStatus.active,
    ))
    db.flush()
    result = ReportService(db).treatment_progress_report()
    assert len(result) == 1
    assert result[0].stages_completed == 1
    assert result[0].current_stage == "adaptation"


def test_treatment_progress_no_plan_shows_zero(db, make_admission):
    make_admission(status=AdmissionStatus.treatment_active)
    result = ReportService(db).treatment_progress_report()
    assert result[0].stages_completed == 0
    assert result[0].current_stage is None
