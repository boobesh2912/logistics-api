from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ShipmentCreate(BaseModel):
    source_address: str
    destination_address: str


class ShipmentStatusUpdate(BaseModel):
    status: str
    location: str


class ShipmentAssignAgent(BaseModel):
    agent_id: UUID


class ShipmentResponse(BaseModel):
    id: UUID
    tracking_number: str
    source_address: str
    destination_address: str
    status: str
    agent_id: Optional[UUID] = None
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


class ShipmentTrackResponse(BaseModel):
    tracking_number: str
    status: str
    current_location: Optional[str] = None

    class Config:
        from_attributes = True