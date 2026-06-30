from typing import Optional
from pydantic import BaseModel, ConfigDict


class RelativeOut(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    id: int
    patient_relative_id: int
    relation_type: str
    id_number: Optional[str] = None
    first_name: str
    last_name: str
    birthdate: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    judicial_situation: Optional[str] = None
    phone: Optional[str] = None
    education_level: Optional[str] = None


class RelativeCreate(BaseModel):
    relation_type: str
    first_name: str
    last_name: str
    id_number: Optional[str] = None
    birthdate: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    judicial_situation: Optional[str] = None
    phone: Optional[str] = None
    education_level: Optional[str] = None


class RelativeUpdate(BaseModel):
    relation_type: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    id_number: Optional[str] = None
    birthdate: Optional[str] = None
    marital_status: Optional[str] = None
    address: Optional[str] = None
    judicial_situation: Optional[str] = None
    phone: Optional[str] = None
    education_level: Optional[str] = None
