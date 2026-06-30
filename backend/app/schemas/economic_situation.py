from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class EconomicSituationOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    has_worked: Optional[bool] = None
    current_job: Optional[str] = None
    work_phone: Optional[str] = None
    workplace: Optional[str] = None
    job_title: Optional[str] = None
    tenure_months: Optional[int] = None
    monthly_income_colones: Optional[float] = None
    house_type: Optional[str] = None
    rent_amount: Optional[float] = None
    family_income_notes: Optional[str] = None
    financial_assistance_notes: Optional[str] = None
    household_members: List[str] = []

    model_config = ConfigDict(from_attributes=False)


class EconomicSituationUpsert(BaseModel):
    has_worked: Optional[bool] = None
    current_job: Optional[str] = None
    work_phone: Optional[str] = None
    workplace: Optional[str] = None
    job_title: Optional[str] = None
    tenure_months: Optional[int] = None
    monthly_income_colones: Optional[float] = None
    house_type: Optional[str] = None
    rent_amount: Optional[float] = None
    family_income_notes: Optional[str] = None
    financial_assistance_notes: Optional[str] = None
    household_members: List[str] = []
