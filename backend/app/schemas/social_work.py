from typing import Optional
from pydantic import BaseModel, ConfigDict


class SocialWorkAssessmentOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    social_worker_id: Optional[int] = None
    assessment_date: Optional[str] = None
    diagnostic_impression: Optional[str] = None
    initial_assessment: Optional[str] = None
    completion_status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class SocialWorkAssessmentUpsert(BaseModel):
    assessment_date: Optional[str] = None
    diagnostic_impression: Optional[str] = None
    initial_assessment: Optional[str] = None
    completion_status: str = "pending"
