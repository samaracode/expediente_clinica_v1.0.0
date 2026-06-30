import pytest
from fastapi import HTTPException

from app.services.export_service import ExportService


def test_get_context_admission_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ExportService(db).get_admission_export_context(9999)
    assert exc.value.status_code == 404


def test_get_context_deleted_admission_raises_404(db, make_admission):
    a = make_admission(is_deleted=True)
    with pytest.raises(HTTPException) as exc:
        ExportService(db).get_admission_export_context(a.id)
    assert exc.value.status_code == 404


def test_get_context_returns_required_keys(db, make_admission):
    a = make_admission()
    ctx = ExportService(db).get_admission_export_context(a.id)
    required_keys = {
        "admission", "resident", "relatives", "consents",
        "economic", "medical", "therapeutic", "social_work",
        "psychology", "occupational", "treatment_plan",
        "daily_logs", "consultations",
        "status_label", "sex_label", "marital_label",
    }
    assert required_keys.issubset(ctx.keys())


def test_get_context_admission_matches(db, make_admission):
    a = make_admission()
    ctx = ExportService(db).get_admission_export_context(a.id)
    assert ctx["admission"].id == a.id


def test_get_context_resident_matches(db, make_resident, make_admission):
    r = make_resident(first_name="Marcos", last_name="Jiménez")
    a = make_admission(resident=r)
    ctx = ExportService(db).get_admission_export_context(a.id)
    assert ctx["resident"].first_name == "Marcos"
    assert ctx["resident"].last_name == "Jiménez"


def test_get_context_empty_relations_are_lists_or_none(db, make_admission):
    a = make_admission()
    ctx = ExportService(db).get_admission_export_context(a.id)
    assert isinstance(ctx["relatives"], list)
    assert isinstance(ctx["consents"], list)
    assert isinstance(ctx["daily_logs"], list)
    assert isinstance(ctx["consultations"], list)
    assert ctx["medical"] is None
    assert ctx["therapeutic"] is None
    assert ctx["treatment_plan"] is None


def test_get_context_status_label_translated(db, make_admission):
    from app.models.admission import AdmissionStatus
    a = make_admission(status=AdmissionStatus.treatment_active)
    ctx = ExportService(db).get_admission_export_context(a.id)
    assert ctx["status_label"] == "Tratamiento activo"


def test_get_context_sex_label_unknown_returns_dash(db, make_admission):
    a = make_admission()
    ctx = ExportService(db).get_admission_export_context(a.id)
    assert ctx["sex_label"] == "—"
