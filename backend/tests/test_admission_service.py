import pytest
from datetime import date
from fastapi import HTTPException

from app.models.admission import AdmissionStatus
from app.schemas.admission import AdmissionCreate, AdmissionStatusUpdate
from app.services.admission_service import AdmissionService


def test_create_generates_admission_number(db, make_resident):
    r = make_resident()
    data = AdmissionCreate(resident_id=r.id, admission_date=date(2024, 1, 1))
    result = AdmissionService(db).create(data)
    assert result.admission_number == "ADM-00001"


def test_create_increments_number(db, make_resident, make_admission):
    r = make_resident()
    make_admission(resident=r)  # ADM-00001 exists
    r2 = make_resident(first_name="Otro")
    data = AdmissionCreate(resident_id=r2.id, admission_date=date(2024, 2, 1))
    result = AdmissionService(db).create(data)
    assert result.admission_number == "ADM-00002"


def test_create_resident_not_found_raises_404(db):
    data = AdmissionCreate(resident_id=9999, admission_date=date(2024, 1, 1))
    with pytest.raises(HTTPException) as exc:
        AdmissionService(db).create(data)
    assert exc.value.status_code == 404


def test_get_returns_admission(db, make_admission):
    a = make_admission()
    result = AdmissionService(db).get(a.id)
    assert result.id == a.id


def test_get_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        AdmissionService(db).get(9999)
    assert exc.value.status_code == 404


def test_list_by_resident_returns_admissions(db, make_resident, make_admission):
    r = make_resident()
    make_admission(resident=r)
    make_admission(resident=r)
    result = AdmissionService(db).list_by_resident(r.id)
    assert len(result) == 2


def test_list_by_resident_excludes_archived(db, make_resident, make_admission):
    r = make_resident()
    make_admission(resident=r)
    make_admission(resident=r, is_deleted=True)
    result = AdmissionService(db).list_by_resident(r.id)
    assert len(result) == 1


def test_list_by_resident_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        AdmissionService(db).list_by_resident(9999)
    assert exc.value.status_code == 404


def test_list_by_resident_only_returns_own(db, make_resident, make_admission):
    r1 = make_resident()
    r2 = make_resident(first_name="Otro")
    make_admission(resident=r1)
    make_admission(resident=r2)
    result = AdmissionService(db).list_by_resident(r1.id)
    assert len(result) == 1
    assert result[0].resident_id == r1.id


def test_archive_soft_deletes(db, make_admission):
    a = make_admission()
    AdmissionService(db).archive(a.id)
    db.refresh(a)
    assert a.is_deleted is True
    assert a.deleted_at is not None


def test_archive_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        AdmissionService(db).archive(9999)
    assert exc.value.status_code == 404


def test_update_status(db, make_admission):
    a = make_admission(status=AdmissionStatus.intake_pending)
    data = AdmissionStatusUpdate(status=AdmissionStatus.treatment_active)
    result = AdmissionService(db).update_status(a.id, data)
    assert result.status == AdmissionStatus.treatment_active


def test_update_status_not_found_raises_404(db):
    data = AdmissionStatusUpdate(status=AdmissionStatus.discharged)
    with pytest.raises(HTTPException) as exc:
        AdmissionService(db).update_status(9999, data)
    assert exc.value.status_code == 404
