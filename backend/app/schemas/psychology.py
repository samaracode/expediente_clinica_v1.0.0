from typing import Optional
from pydantic import BaseModel, ConfigDict


class PsychologyAssessmentOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    psychologist_id: Optional[int] = None
    assessment_date: Optional[str] = None
    initial_diagnostic_impression: Optional[str] = None
    observable_assessment: Optional[str] = None
    diagnostic_tests_notes: Optional[str] = None
    completion_status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class PsychologyAssessmentUpsert(BaseModel):
    assessment_date: Optional[str] = None
    initial_diagnostic_impression: Optional[str] = None
    observable_assessment: Optional[str] = None
    diagnostic_tests_notes: Optional[str] = None
    completion_status: str = "pending"
