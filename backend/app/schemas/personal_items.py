from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PersonalItem(BaseModel):
    description: str
    quantity: int = 1
    condition: Optional[str] = None


class PersonalItemsInventoryOut(BaseModel):
    id: Optional[int] = None
    admission_id: int
    recorded_at: Optional[datetime] = None
    recorded_by_user_id: Optional[int] = None
    items: List[PersonalItem] = []
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PersonalItemsInventoryUpsert(BaseModel):
    items: List[PersonalItem] = []
    notes: Optional[str] = None
