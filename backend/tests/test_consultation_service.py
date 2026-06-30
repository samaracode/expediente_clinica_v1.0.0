import pytest
from fastapi import HTTPException

from app.schemas.consultations import ConsultationCreate, ConsultationUpdate
from app.services.consultation_service import ConsultationService


def test_list_returns_consultations(db, make_admission):
    from app.models.follow_up import Consultation
    from datetime import date as d
    a = make_admission()
    c = Consultation(admission_id=a.id, consultation_date=d(2024, 3, 1))
    db.add(c)
    db.flush()
    result = ConsultationService(db).list(a.id)
    assert len(result) == 1


def test_list_excludes_deleted(db, make_admission):
    from app.models.follow_up import Consultation
    from datetime import date as d
    a = make_admission()
    c = Consultation(admission_id=a.id, consultation_date=d(2024, 3, 1), is_deleted=True)
    db.add(c)
    db.flush()
    result = ConsultationService(db).list(a.id)
    assert len(result) == 0


def test_list_admission_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ConsultationService(db).list(9999)
    assert exc.value.status_code == 404


def test_list_filters_by_area(db, make_admission):
    from app.models.follow_up import Consultation
    from datetime import date as d
    a = make_admission()
    db.add(Consultation(admission_id=a.id, consultation_date=d(2024, 3, 1), area_id=1))
    db.add(Consultation(admission_id=a.id, consultation_date=d(2024, 3, 2), area_id=2))
    db.flush()
    result = ConsultationService(db).list(a.id, area_id=1)
    assert len(result) == 1


def test_create_consultation(db, make_admission):
    a = make_admission()
    body = ConsultationCreate(consultation_date="2024-04-15", consultation_type="médica")
    result = ConsultationService(db).create(a.id, body)
    assert result.admission_id == a.id
    assert result.consultation_date == "2024-04-15"
    assert result.consultation_type == "médica"


def test_create_with_next_appointment(db, make_admission):
    a = make_admission()
    body = ConsultationCreate(
        consultation_date="2024-04-15",
        next_appointment_date="2024-05-01",
    )
    result = ConsultationService(db).create(a.id, body)
    assert result.next_appointment_date == "2024-05-01"


def test_create_admission_not_found_raises_404(db):
    body = ConsultationCreate(consultation_date="2024-04-15")
    with pytest.raises(HTTPException) as exc:
        ConsultationService(db).create(9999, body)
    assert exc.value.status_code == 404


def test_update_consultation(db, make_admission):
    from app.models.follow_up import Consultation
    from datetime import date as d
    a = make_admission()
    c = Consultation(admission_id=a.id, consultation_date=d(2024, 3, 1))
    db.add(c)
    db.flush()
    result = ConsultationService(db).update(c.id, ConsultationUpdate(consultation_type="psicológica"))
    assert result.consultation_type == "psicológica"


def test_update_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ConsultationService(db).update(9999, ConsultationUpdate(consultation_type="x"))
    assert exc.value.status_code == 404


def test_delete_soft_deletes(db, make_admission):
    from app.models.follow_up import Consultation
    from datetime import date as d
    a = make_admission()
    c = Consultation(admission_id=a.id, consultation_date=d(2024, 3, 1))
    db.add(c)
    db.flush()
    ConsultationService(db).delete(c.id)
    db.refresh(c)
    assert c.is_deleted is True


def test_delete_not_found_raises_404(db):
    with pytest.raises(HTTPException) as exc:
        ConsultationService(db).delete(9999)
    assert exc.value.status_code == 404
