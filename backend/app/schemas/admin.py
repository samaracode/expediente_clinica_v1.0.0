from typing import List, Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserAdminOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: Optional[str] = None
    modules: List[str] = []
    model_config = ConfigDict(from_attributes=False)


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    role: str = "counselor"
    password: str
    modules: List[str] = []


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    modules: Optional[List[str]] = None


class PasswordResetIn(BaseModel):
    new_password: str


class TreatmentAreaOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProfessionalOut(BaseModel):
    id: int
    user_id: int
    area_id: int
    first_name: str
    last_name: str
    specialty: Optional[str] = None
    is_active: bool
    area_name: Optional[str] = None
    user_email: Optional[str] = None
    model_config = ConfigDict(from_attributes=False)


class ProfessionalCreate(BaseModel):
    user_id: int
    area_id: int
    first_name: str
    last_name: str
    specialty: Optional[str] = None


class ProfessionalUpdate(BaseModel):
    area_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialty: Optional[str] = None
    is_active: Optional[bool] = None
