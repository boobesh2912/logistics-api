from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.shipment_repository import get_shipment_by_id
from app.repositories.tracking_repository import create_tracking_update


def add_tracking_update(db: Session, shipment_id, data: dict, current_user):
    shipment = get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if str(shipment.agent_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not assigned to this shipment")

    tracking_data = {
        "shipment_id": shipment_id,
        "location": data["location"],
        "status": data["status"]
    }
    return create_tracking_update(db, tracking_data)