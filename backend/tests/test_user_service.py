import pytest
from fastapi import HTTPException

from app.models.user import User, UserRole
from app.schemas.admin import UserCreate, UserUpdate
from app.services.user_service import UserService


def test_list_all_returns_users(db, make_user):
    make_user()
    make_user(email="second@test.com")
    result = UserService(db).list_all()
    assert len(result) == 2


def test_list_all_empty(db):
    result = UserService(db).list_all()
    assert result == []


def test_create_user_returns_correct_fields(db):
    data = UserCreate(full_name="Nuevo", email="nuevo@test.com", role="counselor", password="secret")
    result = UserService(db).create(data)
    assert result.email == "nuevo@test.com"
    assert result.role == "counselor"
    assert result.is_active is True


def test_create_hashes_password(db):
    data = UserCreate(full_name="Test", email="test@test.com", role="admin", password="plaintext")
    UserService(db).create(data)
    user = db.query(User).filter(User.email == "test@test.com").first()
    assert user.hashed_password != "plaintext"
    assert len(user.hashed_password) > 20


def test_create_duplicate_email_raises_400(db, make_user):
    make_user(email="dup@test.com")
    data = UserCreate(full_name="Otro", email="dup@test.com", role="counselor", password="pass")
    with pytest.raises(HTTPException) as exc:
        UserService(db).create(data)
    assert exc.value.status_code == 400


def test_create_invalid_role_raises_422(db):
    data = UserCreate(full_name="X", email="x@test.com", role="superadmin", password="pass")
    with pytest.raises(HTTPException) as exc:
        UserService(db).create(data)
    assert exc.value.status_code == 422


def test_update_full_name(db, make_user):
    u = make_user(full_name="Original")
    admin = make_user(email="admin@test.com")
    result = UserService(db).update(u.id, UserUpdate(full_name="Nuevo Nombre"), admin)
    assert result.full_name == "Nuevo Nombre"


def test_update_role(db, make_user):
    u = make_user(role=UserRole.counselor)
    admin = make_user(email="admin@test.com")
    result = UserService(db).update(u.id, UserUpdate(role="medical"), admin)
    assert result.role == "medical"


def test_update_deactivate_other_user(db, make_user):
    target = make_user()
    admin = make_user(email="admin@test.com")
    result = UserService(db).update(target.id, UserUpdate(is_active=False), admin)
    assert result.is_active is False


def test_update_invalid_role_raises_422(db, make_user):
    u = make_user()
    admin = make_user(email="admin@test.com")
    with pytest.raises(HTTPException) as exc:
        UserService(db).update(u.id, UserUpdate(role="invalid_role"), admin)
    assert exc.value.status_code == 422


def test_update_cannot_self_deactivate(db, make_user):
    admin = make_user()
    with pytest.raises(HTTPException) as exc:
        UserService(db).update(admin.id, UserUpdate(is_active=False), admin)
    assert exc.value.status_code == 400


def test_update_not_found_raises_404(db, make_user):
    admin = make_user()
    with pytest.raises(HTTPException) as exc:
        UserService(db).update(9999, UserUpdate(full_name="X"), admin)
    assert exc.value.status_code == 404
