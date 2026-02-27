from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.services.shipment_service import (
    create_new_shipment,
    track_shipment,
    get_my_shipments,
    update_status_service,
    assign_agent_service,
    cancel_shipment
)
from app.schemas.shipment_schema import (
    ShipmentCreate,
    ShipmentResponse,
    ShipmentTrackResponse,
    ShipmentStatusUpdate,
    ShipmentAssignAgent
)

router = APIRouter(prefix="/shipments", tags=["Shipments"])


# Customer - Create shipment
@router.post("/", response_model=ShipmentResponse, status_code=201)
def create_shipment(
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return create_new_shipment(db, data.model_dump(), current_user.id)


# Customer - View all my shipments
@router.get("/", response_model=List[ShipmentResponse])
def list_shipments(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return get_my_shipments(db, current_user.id)


# Any auth user - Track shipment by tracking number
@router.get("/{tracking_number}", response_model=ShipmentTrackResponse)
def track(
    tracking_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return track_shipment(db, tracking_number)


# Agent - Update shipment status
@router.put("/{shipment_id}/status", response_model=ShipmentResponse)
def update_status(
    shipment_id: UUID,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("agent"))
):
    return update_status_service(db, shipment_id, data.model_dump(), current_user)


# Admin - Assign agent to shipment
@router.put("/{shipment_id}/assign-agent", response_model=ShipmentResponse)
def assign_agent(
    shipment_id: UUID,
    data: ShipmentAssignAgent,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return assign_agent_service(db, shipment_id, data.agent_id, current_user)


# Customer - Cancel shipment
@router.delete("/{shipment_id}")
def cancel(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return cancel_shipment(db, shipment_id, current_user.id)