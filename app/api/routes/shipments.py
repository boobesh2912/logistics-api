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
    cancel_shipment
)
from app.schemas.shipment_schema import ShipmentCreate, ShipmentResponse, ShipmentTrackResponse

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.post("/", response_model=ShipmentResponse, status_code=201)
def create_shipment(
    data: ShipmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return create_new_shipment(db, data.dict(), current_user.id)


@router.get("/", response_model=List[ShipmentResponse])
def list_shipments(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return get_my_shipments(db, current_user.id)


@router.get("/{tracking_number}", response_model=ShipmentTrackResponse)
def track(
    tracking_number: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return track_shipment(db, tracking_number)


@router.delete("/{shipment_id}")
def cancel(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("customer"))
):
    return cancel_shipment(db, shipment_id, current_user.id)