from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ShipmentCreate(BaseModel):
    source_address: str
    destination_address: str


class ShipmentResponse(BaseModel):
    id: UUID
    tracking_number: str
    source_address: str
    destination_address: str
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ShipmentTrackResponse(BaseModel):
    tracking_number: str
    status: str
    current_location: Optional[str] = None

    class Config:
        from_attributes = True