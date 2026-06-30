from typing import Optional
from pydantic import BaseModel, ConfigDict


class TherapeuticAssessmentOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    assessor_id: Optional[int] = None
    assessment_date: Optional[str] = None
    initial_summary: Optional[str] = None
    clinical_history_summary: Optional[str] = None
    europal_si_notes: Optional[str] = None
    socrates_notes: Optional[str] = None
    urica_notes: Optional[str] = None
    afc_analysis_notes: Optional[str] = None
    relapse_prevention_interview: Optional[str] = None
    relapse_prevention_plan: Optional[str] = None
    completion_status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class TherapeuticAssessmentUpsert(BaseModel):
    assessment_date: Optional[str] = None
    initial_summary: Optional[str] = None
    clinical_history_summary: Optional[str] = None
    europal_si_notes: Optional[str] = None
    socrates_notes: Optional[str] = None
    urica_notes: Optional[str] = None
    afc_analysis_notes: Optional[str] = None
    relapse_prevention_interview: Optional[str] = None
    relapse_prevention_plan: Optional[str] = None
    completion_status: str = "pending"
