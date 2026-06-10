from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConsultationOut(BaseModel):
    model_config = ConfigDict(from_attributes=False)

    id: int
    admission_id: int
    professional_id: Optional[int] = None
    area_id: Optional[int] = None
    consultation_type: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    consultation_date: str
    next_appointment_date: Optional[str] = None
    professional_name: Optional[str] = None
    area_name: Optional[str] = None


class ConsultationCreate(BaseModel):
    consultation_date: str
    professional_id: Optional[int] = None
    area_id: Optional[int] = None
    consultation_type: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    next_appointment_date: Optional[str] = None


class ConsultationUpdate(BaseModel):
    consultation_date: Optional[str] = None
    professional_id: Optional[int] = None
    area_id: Optional[int] = None
    consultation_type: Optional[str] = None
    description: Optional[str] = None
    observations: Optional[str] = None
    next_appointment_date: Optional[str] = None
