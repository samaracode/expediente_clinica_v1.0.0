from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel
from app.models.admission import AdmissionStatus, AdmissionType


class AdmissionCreate(BaseModel):
    resident_id: int
    admission_type: AdmissionType = AdmissionType.first
    admission_date: date
    assigned_counselor_id: Optional[int] = None
    referral_source: Optional[str] = None
    admission_condition: Optional[str] = None
    initial_diagnosis: Optional[str] = None
    sponsor_name: Optional[str] = None
    sponsor_relationship: Optional[str] = None
    sponsor_phone: Optional[str] = None
    sponsor_address: Optional[str] = None
    judicial_status: Optional[str] = None
    has_support_network: bool = False


class AdmissionStatusUpdate(BaseModel):
    status: AdmissionStatus


class AdmissionOut(BaseModel):
    id: int
    admission_number: str
    resident_id: int
    admission_type: AdmissionType
    admission_date: date
    discharge_date: Optional[date] = None
    status: AdmissionStatus
    referral_source: Optional[str] = None
    admission_condition: Optional[str] = None
    initial_diagnosis: Optional[str] = None
    sponsor_name: Optional[str] = None
    sponsor_phone: Optional[str] = None
    judicial_status: Optional[str] = None
    has_support_network: bool
    assigned_counselor_id: Optional[int] = None
    is_deleted: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
