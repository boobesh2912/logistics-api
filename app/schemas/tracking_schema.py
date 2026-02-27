from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class TrackingCreate(BaseModel):
    location: str
    status: str


class TrackingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    shipment_id: UUID
    location: str
    status: str
    updated_at: datetime