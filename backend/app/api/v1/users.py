from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import RoleRequired, get_current_user
from app.core.security import get_password_hash
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.admin import UserAdminOut, UserCreate, UserUpdate

router = APIRouter()

_admin_only = RoleRequired(["admin"])


def _build_out(u: User) -> UserAdminOut:
    return UserAdminOut(
        id=u.id,
        full_name=u.full_name,
        email=u.email,
        role=u.role.value if isinstance(u.role, UserRole) else u.role,
        is_active=u.is_active,
        created_at=u.created_at.isoformat() if u.created_at else None,
    )


@router.get("/", response_model=List[UserAdminOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    users = db.query(User).order_by(User.full_name).all()
    return [_build_out(u) for u in users]


@router.post("/", response_model=UserAdminOut, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(_admin_only),
):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    try:
        role = UserRole(data.role)
    except ValueError:
        raise HTTPException(status_code=422, detail="Rol inválido")

    user = User(
        full_name=data.full_name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _build_out(user)


@router.put("/{user_id}", response_model=UserAdminOut)
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(_admin_only),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        try:
            user.role = UserRole(data.role)
        except ValueError:
            raise HTTPException(status_code=422, detail="Rol inválido")
    if data.is_active is not None:
        if user.id == current_admin.id and data.is_active is False:
            raise HTTPException(status_code=400, detail="No puedes desactivar tu propio usuario")
        user.is_active = data.is_active

    db.commit()
    db.refresh(user)
    return _build_out(user)
