import pytest
from fastapi import HTTPException

from app.schemas.treatment import TreatmentPlanUpsert, TreatmentStageUpsert
from app.services.treatment_service import TreatmentService


def test_get_plan_returns_empty_when_no_plan(db, make_admission):
    a = make_admission()
    result = TreatmentService(db).get_plan(a.id)
    assert result.id is None
    assert result.admission_id == a.id
    assert len(result.stages) == 5  # all 5 default stages


def test_get_plan_admission_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        TreatmentService(db).get_plan(9999)
    assert exc.value.status_code == 404


def test_get_plan_returns_existing_plan(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    data = TreatmentPlanUpsert(recommendations="Descanso y terapia")
    TreatmentService(db).upsert_plan(a.id, data, user)
    result = TreatmentService(db).get_plan(a.id)
    assert result.id is not None
    assert result.recommendations == "Descanso y terapia"


def test_upsert_creates_new_plan(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    data = TreatmentPlanUpsert(plan_details="Detalles del plan", life_project="Proyecto de vida")
    result = TreatmentService(db).upsert_plan(a.id, data, user)
    assert result.id is not None
    assert result.plan_details == "Detalles del plan"
    assert result.life_project == "Proyecto de vida"


def test_upsert_updates_existing_plan(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(recommendations="V1"), user)
    result = TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(recommendations="V2"), user)
    assert result.recommendations == "V2"


def test_upsert_creates_stages(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    stages = [
        TreatmentStageUpsert(stage_name="orientation", status="active", start_date="2024-01-01"),
        TreatmentStageUpsert(stage_name="adaptation", status="pending"),
    ]
    result = TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(stages=stages), user)
    stage_names = [s.stage_name for s in result.stages]
    assert "orientation" in stage_names
    assert "adaptation" in stage_names


def test_upsert_skips_invalid_stage_name(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    stages = [
        TreatmentStageUpsert(stage_name="invalid_stage", status="active"),
        TreatmentStageUpsert(stage_name="orientation", status="active"),
    ]
    result = TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(stages=stages), user)
    saved_with_id = [s for s in result.stages if s.id is not None]
    assert len(saved_with_id) == 1
    assert saved_with_id[0].stage_name == "orientation"


def test_upsert_updates_existing_stage(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    stages_v1 = [TreatmentStageUpsert(stage_name="orientation", status="active", progress_notes="Inicio")]
    TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(stages=stages_v1), user)

    stages_v2 = [TreatmentStageUpsert(stage_name="orientation", status="completed", progress_notes="Finalizado")]
    result = TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(stages=stages_v2), user)

    orientation = next(s for s in result.stages if s.stage_name == "orientation")
    assert orientation.status == "completed"
    assert orientation.progress_notes == "Finalizado"


def test_upsert_plan_all_stages_present_in_output(db, make_admission, make_user):
    a = make_admission()
    user = make_user()
    result = TreatmentService(db).upsert_plan(a.id, TreatmentPlanUpsert(), user)
    assert len(result.stages) == 5
    stage_names = {s.stage_name for s in result.stages}
    assert stage_names == {"orientation", "adaptation", "development", "consolidation", "reintegration"}


def test_upsert_admission_not_found_raises_404(db, make_user):
    user = make_user()
    with pytest.raises(HTTPException) as exc:
        TreatmentService(db).upsert_plan(9999, TreatmentPlanUpsert(), user)
    assert exc.value.status_code == 404
