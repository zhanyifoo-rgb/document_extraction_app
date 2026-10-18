from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentOut(BaseModel):
    id: UUID
    filename: str
    document_type: str
    status: str
    extracted_data: dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewRequest(BaseModel):
    extracted_data: dict = Field(min_length=1)
    status: str = "approved"