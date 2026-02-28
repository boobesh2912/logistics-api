from pydantic import BaseModel, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tracking_number: str
    customer_id: UUID
    source_address: str
    destination_address: str
    status: str
    agent_id: Optional[UUID] = None
    created_at: Optional[datetime]


class ShipmentTrackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tracking_number: str
    status: str
    current_location: Optional[str] = None
