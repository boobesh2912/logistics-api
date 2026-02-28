import uuid as uuid_lib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.shipment import Shipment
from app.schemas.shipment_schema import (
    ShipmentCreate, ShipmentResponse, ShipmentTrackResponse,
    ShipmentStatusUpdate, ShipmentAssignAgent
)

SHIPMENT_STATUSES = ["created", "in_transit", "out_for_delivery", "delivered"]

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.post("/", response_model=ShipmentResponse, status_code=201)
def create_shipment(
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("customer"))
):
    tracking_number = "TRK" + uuid_lib.uuid4().hex[:8].upper()
    shipment = Shipment(
        tracking_number=tracking_number,
        customer_id=uuid_lib.UUID(current_user["uid"]),
        source_address=data.source_address,
        destination_address=data.destination_address,
        status="created"
    )
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


@router.get("/", response_model=List[ShipmentResponse])
def list_shipments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("customer"))
):
    customer_id = uuid_lib.UUID(current_user["uid"])
    return db.query(Shipment).filter(Shipment.customer_id == customer_id).all()


@router.get("/{tracking_number}", response_model=ShipmentTrackResponse)
def track_shipment(
    tracking_number: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    shipment = db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return {"tracking_number": shipment.tracking_number, "status": shipment.status, "current_location": shipment.current_location}


@router.put("/{shipment_id}/status", response_model=ShipmentResponse)
def update_status(
    shipment_id: UUID,
    data: ShipmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("agent"))
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    agent_id = uuid_lib.UUID(current_user["uid"])
    if str(shipment.agent_id) != str(agent_id):
        raise HTTPException(status_code=403, detail="You are not assigned to this shipment")
    if data.status not in SHIPMENT_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {SHIPMENT_STATUSES}")
    current_index = SHIPMENT_STATUSES.index(shipment.status)
    new_index = SHIPMENT_STATUSES.index(data.status)
    if new_index != current_index + 1:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition. Current status is '{shipment.status}'. Next allowed: '{SHIPMENT_STATUSES[current_index + 1]}'"
        )
    shipment.status = data.status
    shipment.current_location = data.location
    db.commit()
    db.refresh(shipment)
    return shipment


@router.put("/{shipment_id}/assign-agent", response_model=ShipmentResponse)
def assign_agent(
    shipment_id: UUID,
    data: ShipmentAssignAgent,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment.agent_id = data.agent_id
    db.commit()
    db.refresh(shipment)
    return shipment


@router.delete("/{shipment_id}")
def cancel_shipment(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("customer"))
):
    shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    customer_id = uuid_lib.UUID(current_user["uid"])
    if str(shipment.customer_id) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")
    if shipment.status != "created":
        raise HTTPException(status_code=400, detail="Cannot cancel a shipment that is already dispatched")
    db.delete(shipment)
    db.commit()
    return {"message": "Shipment cancelled successfully"}
