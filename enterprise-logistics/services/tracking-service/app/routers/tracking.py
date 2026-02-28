from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.dependencies import require_role, get_current_user
from app.models.tracking import TrackingUpdate
from app.schemas.tracking_schema import TrackingCreate, TrackingResponse

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/{shipment_id}", response_model=TrackingResponse, status_code=201)
def add_tracking_update(
    shipment_id: UUID,
    data: TrackingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("agent"))
):
    update = TrackingUpdate(
        shipment_id=shipment_id,
        location=data.location,
        status=data.status
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


@router.get("/{shipment_id}", response_model=List[TrackingResponse])
def get_tracking_history(
    shipment_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    updates = (
        db.query(TrackingUpdate)
        .filter(TrackingUpdate.shipment_id == shipment_id)
        .order_by(TrackingUpdate.updated_at.desc())
        .all()
    )
    if not updates:
        raise HTTPException(status_code=404, detail="No tracking updates found")
    return updates
