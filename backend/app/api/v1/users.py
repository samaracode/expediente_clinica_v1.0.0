from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import RoleRequired
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import PasswordResetIn, UserAdminOut, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter()

_admin_only = RoleRequired(["admin"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)


@router.get("/", response_model=List[UserAdminOut])
def list_users(
    service: UserService = Depends(get_user_service),
    _: User = Depends(_admin_only),
):
    return service.list_all()


@router.post("/", response_model=UserAdminOut, status_code=201)
def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
    _: User = Depends(_admin_only),
):
    return service.create(data)


@router.put("/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_admin: User = Depends(_admin_only),
):
    return service.update(user_id, data, current_admin)


@router.post("/{user_id}/reset-password", response_model=UserAdminOut)
def reset_password(
    user_id: int,
    data: PasswordResetIn,
    service: UserService = Depends(get_user_service),
    current_admin: User = Depends(_admin_only),
):
    return service.reset_password(user_id, data.new_password, current_admin)
