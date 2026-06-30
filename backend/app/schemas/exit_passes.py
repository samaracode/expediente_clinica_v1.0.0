from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ExitPassOut(BaseModel):
    id: int
    admission_id: int
    requested_at: Optional[str] = None
    approved_by_id: Optional[int] = None
    departure_date: Optional[str] = None
    return_date_expected: Optional[str] = None
    return_date_actual: Optional[str] = None
    reason: Optional[str] = None
    narrative: Optional[str] = None
    companion: Optional[str] = None
    pass_type: str = "regular"
    status: str = "pending"
    model_config = ConfigDict(from_attributes=False)


class ExitPassCreate(BaseModel):
    departure_date: Optional[str] = None
    return_date_expected: Optional[str] = None
    reason: Optional[str] = None
    narrative: Optional[str] = None
    companion: Optional[str] = None
    pass_type: str = "regular"


class ExitPassUpdate(BaseModel):
    status: Optional[str] = None
    return_date_actual: Optional[str] = None
    narrative: Optional[str] = None
    companion: Optional[str] = None
