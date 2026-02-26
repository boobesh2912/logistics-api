from sqlalchemy.orm import Session
from app.models.tracking import TrackingUpdate


def create_tracking_update(db: Session, tracking_data: dict) -> TrackingUpdate:
    update = TrackingUpdate(**tracking_data)
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


def get_latest_tracking(db: Session, shipment_id) -> TrackingUpdate | None:
    return (
        db.query(TrackingUpdate)
        .filter(TrackingUpdate.shipment_id == shipment_id)
        .order_by(TrackingUpdate.updated_at.desc())
        .first()
    )