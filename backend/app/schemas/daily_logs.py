from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class DailyLogOut(BaseModel):
    id: int
    admission_id: int
    logged_by_id: Optional[int] = None
    log_date: str
    intervention_type: Optional[str] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None
    model_config = ConfigDict(from_attributes=False)


class DailyLogCreate(BaseModel):
    log_date: str
    intervention_type: Optional[str] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None


class DailyLogUpdate(BaseModel):
    intervention_type: Optional[str] = None
    notes: Optional[str] = None
    recommendations: Optional[str] = None
