import pytest
from fastapi import HTTPException

from app.core.deps import ModuleRequired
from app.models.user import Module, UserModulePermission, UserRole


def test_admin_passes_any_module(make_user):
    admin = make_user(role=UserRole.admin)
    guard = ModuleRequired(Module.finance)
    assert guard(current_user=admin) is admin


def test_non_admin_without_module_raises_403(make_user):
    u = make_user(role=UserRole.psychologist)
    guard = ModuleRequired(Module.finance)
    with pytest.raises(HTTPException) as exc:
        guard(current_user=u)
    assert exc.value.status_code == 403


def test_non_admin_with_module_passes(db, make_user):
    u = make_user(role=UserRole.psychologist)
    db.add(UserModulePermission(user_id=u.id, module=Module.psychology))
    db.commit()
    db.refresh(u)
    guard = ModuleRequired(Module.psychology)
    assert guard(current_user=u) is u
