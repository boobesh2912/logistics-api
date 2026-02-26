from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import require_role
from app.services.tracking_service import add_tracking_update
from app.schemas.tracking_schema import TrackingCreate, TrackingResponse

router = APIRouter(prefix="/tracking", tags=["Tracking"])


# Agent - Add tracking update to shipment
@router.post("/{shipment_id}", response_model=TrackingResponse, status_code=201)
def add_update(
    shipment_id: UUID,
    data: TrackingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("agent"))
):
    return add_tracking_update(db, shipment_id, data.dict(), current_user)