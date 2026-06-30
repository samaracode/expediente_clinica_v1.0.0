from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TreatmentStageOut(BaseModel):
    id: Optional[int] = None
    stage_name: str
    stage_order: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress_notes: Optional[str] = None
    extension_consent_signed: bool = False
    advancement_criteria: Optional[str] = None
    status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class TreatmentPlanOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    recommendations: Optional[str] = None
    plan_details: Optional[str] = None
    life_project: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    stages: List[TreatmentStageOut] = []
    model_config = ConfigDict(from_attributes=False)


class TreatmentStageUpsert(BaseModel):
    stage_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    progress_notes: Optional[str] = None
    extension_consent_signed: bool = False
    advancement_criteria: Optional[str] = None
    status: str = "pending"


class TreatmentPlanUpsert(BaseModel):
    recommendations: Optional[str] = None
    plan_details: Optional[str] = None
    life_project: Optional[str] = None
    stages: List[TreatmentStageUpsert] = []
