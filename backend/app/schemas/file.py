from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class FileOut(BaseModel):
    """Respuesta al subir o consultar un archivo."""

    id: int
    file_name: str
    mime_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    uploaded_by_id: Optional[int] = None
    uploaded_at: Optional[datetime] = None
    url: str

    model_config = ConfigDict(from_attributes=True)
