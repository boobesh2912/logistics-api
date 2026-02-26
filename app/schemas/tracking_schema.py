from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TrackingCreate(BaseModel):
    location: str
    status: str


class TrackingResponse(BaseModel):
    id: UUID
    shipment_id: UUID
    location: str
    status: str
    updated_at: datetime

    class Config:
        from_attributes = True