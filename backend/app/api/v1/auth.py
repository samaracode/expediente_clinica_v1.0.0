from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import PasswordChangeIn, Token, UserLogin, UserOut
from app.services.audit_service import AuditService

router = APIRouter()

COOKIE_NAME = "access_token"


def _user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        modules=sorted(m.value for m in user.allowed_modules()),
    )


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    modules = sorted(m.value for m in user.allowed_modules())
    token = create_access_token(subject=user.id, role=user.role.value, modules=modules)
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,  # "none" en prod cross-site
        secure=settings.COOKIE_SECURE,       # True en prod con HTTPS
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return Token(access_token=token)


@router.post("/logout")
def logout(response: Response):
    # Debe usar los mismos atributos que set_cookie o el navegador
    # no encontrará/borrará la cookie cross-site.
    response.delete_cookie(
        key=COOKIE_NAME,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
    )
    return {"message": "Sesión cerrada"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _user_out(current_user)


@router.post("/change-password")
def change_password(
    data: PasswordChangeIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña actual incorrecta",
        )
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    AuditService(db).log(current_user.id, "UPDATE", "users", current_user.id)
    return {"message": "Contraseña actualizada"}
