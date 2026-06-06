from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
