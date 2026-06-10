from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.consent import ConsentType


class ConsentItem(BaseModel):
    consent_type: ConsentType
    is_signed: bool
    signed_at: Optional[datetime] = None
    verified_by_user_id: Optional[int] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=False)


class ConsentSign(BaseModel):
    notes: Optional[str] = None
    authorized_persons: Optional[Any] = None
