from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import get_db

# Asumiendo que el login usa el flujo estándar de OAuth2 o cookies
# En el plan, se menciona cookie httpOnly, pero también get_current_user con Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    required=False
)

def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> int:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return int(user_id)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

# NOTA: Cuando se agreguen los modelos ORM, esta función buscará el usuario en la BD
def get_current_active_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
) -> dict:
    # Retorna un mock del usuario por ahora, para permitir la compilación y prueba de la API
    # En el futuro:
    # user = db.query(User).filter(User.id == user_id).first()
    # if not user or not user.is_active: raise HTTPException(...)
    return {"id": user_id, "role": "admin", "is_active": True}

class RoleRequired:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict = Depends(get_current_active_user)):
        # En el futuro, current_user será el modelo SQLAlchemy User
        role = current_user.get("role")
        if role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario no tiene permisos suficientes para realizar esta acción",
            )
        return current_user
