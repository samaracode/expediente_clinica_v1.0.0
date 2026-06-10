from typing import Optional
from pydantic import BaseModel, ConfigDict


class AdmissionReportRow(BaseModel):
    id: int
    admission_number: str
    resident_name: str
    admission_date: str
    discharge_date: Optional[str] = None
    status: str
    admission_type: str
    model_config = ConfigDict(from_attributes=False)


class ConsultationReportRow(BaseModel):
    id: int
    consultation_date: str
    professional_name: str
    area_name: Optional[str] = None
    consultation_type: Optional[str] = None
    resident_name: str
    model_config = ConfigDict(from_attributes=False)


class TreatmentProgressRow(BaseModel):
    admission_id: int
    admission_number: str
    resident_name: str
    status: str
    stages_completed: int
    stages_total: int = 5
    current_stage: Optional[str] = None
    model_config = ConfigDict(from_attributes=False)
