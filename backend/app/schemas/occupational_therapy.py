from typing import Optional
from pydantic import BaseModel, ConfigDict


class OccupationalTherapyAssessmentOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    therapist_id: Optional[int] = None
    assessment_date: Optional[str] = None
    initial_diagnostic_impression: Optional[str] = None
    occupational_profile: Optional[str] = None
    completion_status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class OccupationalTherapyAssessmentUpsert(BaseModel):
    assessment_date: Optional[str] = None
    initial_diagnostic_impression: Optional[str] = None
    occupational_profile: Optional[str] = None
    completion_status: str = "pending"
