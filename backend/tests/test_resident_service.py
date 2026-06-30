import pytest
from fastapi import HTTPException

from app.schemas.resident import ResidentCreate, ResidentUpdate
from app.services.resident_service import ResidentService


def test_list_excludes_archived_by_default(db, make_resident):
    make_resident(first_name="Active")
    make_resident(first_name="Archived", is_deleted=True)
    result = ResidentService(db).list_paginated(None, 1, 20, False)
    assert result.total == 1
    assert result.items[0].first_name == "Active"


def test_list_shows_archived_when_flag_true(db, make_resident):
    make_resident()
    make_resident(is_deleted=True)
    result = ResidentService(db).list_paginated(None, 1, 20, True)
    assert result.total == 2


def test_list_filters_by_first_name(db, make_resident):
    make_resident(first_name="Carlos", last_name="López")
    make_resident(first_name="María", last_name="García")
    result = ResidentService(db).list_paginated("carlos", 1, 20, False)
    assert result.total == 1
    assert result.items[0].first_name == "Carlos"


def test_list_filters_by_id_number(db, make_resident):
    make_resident(id_number="111111111")
    make_resident(id_number="999999999")
    result = ResidentService(db).list_paginated("1111", 1, 20, False)
    assert result.total == 1


def test_list_pagination_calculates_pages(db, make_resident):
    for i in range(25):
        make_resident(first_name=f"Res{i}", last_name="Test")
    result = ResidentService(db).list_paginated(None, 1, 10, False)
    assert result.total == 25
    assert result.pages == 3
    assert len(result.items) == 10


def test_list_page_2_returns_correct_slice(db, make_resident):
    for i in range(15):
        make_resident(first_name=f"Res{i:02d}", last_name="Test")
    result = ResidentService(db).list_paginated(None, 2, 10, False)
    assert len(result.items) == 5


def test_create_generates_zoe_code(db):
    data = ResidentCreate(first_name="Ana", last_name="Mora")
    r = ResidentService(db).create(data)
    assert r.code == "ZOE-0001"


def test_create_increments_code(db, make_resident):
    make_resident()  # ZOE-0001 already used in DB, so new one will be ZOE-0002
    data = ResidentCreate(first_name="Pedro", last_name="Ruiz")
    r = ResidentService(db).create(data)
    assert r.code == "ZOE-0002"


def test_create_duplicate_id_number_raises_400(db, make_resident):
    make_resident(id_number="123456789")
    data = ResidentCreate(first_name="Otro", last_name="Soto", id_number="123456789")
    with pytest.raises(HTTPException) as exc:
        ResidentService(db).create(data)
    assert exc.value.status_code == 400


def test_create_without_id_number_allows_duplicates(db):
    data = ResidentCreate(first_name="Sin", last_name="Cedula")
    svc = ResidentService(db)
    r1 = svc.create(data)
    r2 = svc.create(data)
    assert r1.id != r2.id


def test_get_returns_resident(db, make_resident):
    r = make_resident()
    result = ResidentService(db).get(r.id)
    assert result.id == r.id


def test_get_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ResidentService(db).get(9999)
    assert exc.value.status_code == 404


def test_update_modifies_fields(db, make_resident):
    r = make_resident(first_name="Juan")
    updated = ResidentService(db).update(r.id, ResidentUpdate(first_name="Carlos"))
    assert updated.first_name == "Carlos"


def test_update_partial_only_changes_provided_fields(db, make_resident):
    r = make_resident(first_name="Juan", last_name="Pérez")
    updated = ResidentService(db).update(r.id, ResidentUpdate(first_name="Luis"))
    assert updated.last_name == "Pérez"


def test_update_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ResidentService(db).update(9999, ResidentUpdate(first_name="X"))
    assert exc.value.status_code == 404


def test_archive_soft_deletes(db, make_resident):
    r = make_resident()
    ResidentService(db).archive(r.id)
    db.refresh(r)
    assert r.is_deleted is True
    assert r.deleted_at is not None


def test_archive_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ResidentService(db).archive(9999)
    assert exc.value.status_code == 404
