from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.models.resident import Sex, MaritalStatus


class ResidentCreate(BaseModel):
    first_name: str
    last_name: str
    id_number: Optional[str] = None
    birthdate: Optional[date] = None
    sex: Optional[Sex] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = None
    province: Optional[str] = None
    canton: Optional[str] = None
    district: Optional[str] = None
    neighborhood: Optional[str] = None
    address_other: Optional[str] = None
    phone_home: Optional[str] = None
    phone_mobile: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_insured: bool = False
    insurance_type: Optional[str] = None


class ResidentUpdate(ResidentCreate):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ResidentOut(BaseModel):
    id: int
    code: str
    first_name: str
    last_name: str
    id_number: Optional[str] = None
    birthdate: Optional[date] = None
    sex: Optional[Sex] = None
    marital_status: Optional[MaritalStatus] = None
    nationality: Optional[str] = None
    province: Optional[str] = None
    canton: Optional[str] = None
    district: Optional[str] = None
    phone_mobile: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    is_insured: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ResidentList(BaseModel):
    id: int
    code: str
    first_name: str
    last_name: str
    id_number: Optional[str] = None
    phone_mobile: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
