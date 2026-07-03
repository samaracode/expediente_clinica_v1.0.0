from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import Module, User, UserModulePermission, UserRole
from app.schemas.admin import UserAdminOut, UserCreate, UserUpdate
from app.services.audit_service import AuditService


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def _build_out(self, u: User) -> UserAdminOut:
        return UserAdminOut(
            id=u.id,
            full_name=u.full_name,
            email=u.email,
            role=u.role.value if isinstance(u.role, UserRole) else u.role,
            is_active=u.is_active,
            created_at=u.created_at.isoformat() if u.created_at else None,
            modules=sorted(m.value for m in u.allowed_modules()),
        )

    def _get_or_404(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user

    def _parse_modules(self, modules: List[str]) -> List[Module]:
        try:
            return [Module(m) for m in modules]
        except ValueError:
            raise HTTPException(status_code=422, detail="Módulo inválido")

    def _set_modules(self, user: User, modules: List[Module]) -> None:
        """Reemplaza los permisos de módulo del usuario. admin no necesita
        filas (acceso total implícito, ver User.allowed_modules)."""
        self.db.query(UserModulePermission).filter(
            UserModulePermission.user_id == user.id
        ).delete()
        for module in set(modules):
            self.db.add(UserModulePermission(user_id=user.id, module=module))

    def list_all(self) -> List[UserAdminOut]:
        users = self.db.query(User).order_by(User.full_name).all()
        return [self._build_out(u) for u in users]

    def create(self, data: UserCreate) -> UserAdminOut:
        if self.db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="El email ya está registrado")
        try:
            role = UserRole(data.role)
        except ValueError:
            raise HTTPException(status_code=422, detail="Rol inválido")
        modules = self._parse_modules(data.modules)
        user = User(
            full_name=data.full_name,
            email=data.email,
            hashed_password=get_password_hash(data.password),
            role=role,
            is_active=True,
        )
        self.db.add(user)
        self.db.flush()
        self._set_modules(user, modules)
        self.db.commit()
        self.db.refresh(user)
        return self._build_out(user)

    def update(self, user_id: int, data: UserUpdate, current_admin: User) -> UserAdminOut:
        user = self._get_or_404(user_id)
        audit = AuditService(self.db)
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.role is not None:
            try:
                user.role = UserRole(data.role)
            except ValueError:
                raise HTTPException(status_code=422, detail="Rol inválido")
            audit.log(current_admin.id, "UPDATE", "users", user.id)
        if data.is_active is not None:
            if user.id == current_admin.id and data.is_active is False:
                raise HTTPException(
                    status_code=400, detail="No puedes desactivar tu propio usuario"
                )
            user.is_active = data.is_active
            audit.log(current_admin.id, "UPDATE", "users", user.id)
        if data.modules is not None:
            modules = self._parse_modules(data.modules)
            self._set_modules(user, modules)
            audit.log(current_admin.id, "UPDATE", "user_module_permissions", user.id)
        self.db.commit()
        self.db.refresh(user)
        return self._build_out(user)

    def reset_password(
        self, user_id: int, new_password: str, current_admin: User
    ) -> UserAdminOut:
        user = self._get_or_404(user_id)
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        AuditService(self.db).log(current_admin.id, "UPDATE", "users", user.id)
        return self._build_out(user)
