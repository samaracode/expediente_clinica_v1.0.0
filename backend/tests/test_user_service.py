import pytest
from fastapi import HTTPException

from app.models.audit import AuditLog
from app.models.user import Module, User, UserModulePermission, UserRole
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


# --- Permisos de módulo (ADR 0003) ---

def test_admin_has_all_modules_without_rows(db, make_user):
    admin = make_user(role=UserRole.admin)
    assert admin.allowed_modules() == set(Module)
    assert admin.has_module(Module.finance)
    assert admin.has_module(Module.medical)


def test_non_admin_has_no_modules_by_default(db, make_user):
    u = make_user(role=UserRole.psychologist)
    assert u.allowed_modules() == set()
    assert not u.has_module(Module.psychology)


def test_create_user_with_modules(db):
    data = UserCreate(
        full_name="Psico",
        email="psico@test.com",
        role="psychologist",
        password="pass",
        modules=["psychology", "residents"],
    )
    result = UserService(db).create(data)
    assert set(result.modules) == {"psychology", "residents"}
    user = db.query(User).filter(User.email == "psico@test.com").first()
    assert user.has_module(Module.psychology)
    assert not user.has_module(Module.finance)


def test_update_modules_replaces_previous(db, make_user):
    u = make_user(role=UserRole.psychologist)
    admin = make_user(email="admin2@test.com", role=UserRole.admin)
    UserService(db).update(u.id, UserUpdate(modules=["psychology"]), admin)
    result = UserService(db).update(u.id, UserUpdate(modules=["residents", "reports"]), admin)
    assert set(result.modules) == {"residents", "reports"}
    remaining = db.query(UserModulePermission).filter(UserModulePermission.user_id == u.id).all()
    assert {r.module for r in remaining} == {Module.residents, Module.reports}


def test_update_invalid_module_raises_422(db, make_user):
    u = make_user()
    admin = make_user(email="admin3@test.com")
    with pytest.raises(HTTPException) as exc:
        UserService(db).update(u.id, UserUpdate(modules=["not_a_module"]), admin)
    assert exc.value.status_code == 422


def test_update_modules_logs_audit(db, make_user):
    u = make_user(role=UserRole.psychologist)
    admin = make_user(email="admin4@test.com", role=UserRole.admin)
    UserService(db).update(u.id, UserUpdate(modules=["psychology"]), admin)
    logs = db.query(AuditLog).filter(AuditLog.table_affected == "user_module_permissions").all()
    assert len(logs) == 1
    assert logs[0].user_id == admin.id
    assert logs[0].record_id == u.id


# --- Reset de contraseña por admin ---

def test_reset_password_changes_hash_and_logs_audit(db, make_user):
    u = make_user()
    original_hash = u.hashed_password
    admin = make_user(email="admin5@test.com", role=UserRole.admin)
    UserService(db).reset_password(u.id, "nueva_clave_temporal", admin)
    db.refresh(u)
    assert u.hashed_password != original_hash
    logs = db.query(AuditLog).filter(AuditLog.table_affected == "users").all()
    assert any(log.record_id == u.id for log in logs)


def test_reset_password_not_found_raises_404(db, make_user):
    admin = make_user()
    with pytest.raises(HTTPException) as exc:
        UserService(db).reset_password(9999, "x", admin)
    assert exc.value.status_code == 404


def test_update_role_logs_audit(db, make_user):
    u = make_user(role=UserRole.counselor)
    admin = make_user(email="admin6@test.com", role=UserRole.admin)
    UserService(db).update(u.id, UserUpdate(role="medical"), admin)
    logs = db.query(AuditLog).filter(AuditLog.table_affected == "users", AuditLog.record_id == u.id).all()
    assert len(logs) >= 1
