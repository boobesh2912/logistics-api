import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.shipment_repository import (
    create_shipment,
    get_shipment_by_tracking_number,
    get_shipment_by_id,
    get_all_shipments_by_customer,
    delete_shipment
)
from app.repositories.tracking_repository import get_latest_tracking


def create_new_shipment(db: Session, data: dict, customer_id):
    tracking_number = "TRK" + uuid.uuid4().hex[:8].upper()
    shipment_data = {
        "tracking_number": tracking_number,
        "customer_id": customer_id,
        "source_address": data["source_address"],
        "destination_address": data["destination_address"],
        "status": "created"
    }
    return create_shipment(db, shipment_data)


def track_shipment(db: Session, tracking_number: str):
    shipment = get_shipment_by_tracking_number(db, tracking_number)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    latest = get_latest_tracking(db, shipment.id)
    return {
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "current_location": latest.location if latest else None
    }


def get_my_shipments(db: Session, customer_id):
    return get_all_shipments_by_customer(db, customer_id)


def cancel_shipment(db: Session, shipment_id, customer_id):
    shipment = get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if str(shipment.customer_id) != str(customer_id):
        raise HTTPException(status_code=403, detail="Access denied")

    if shipment.status != "created":
        raise HTTPException(status_code=400, detail="Cannot cancel a shipment that is already dispatched")

    delete_shipment(db, shipment)
    return {"message": "Shipment cancelled successfully"}