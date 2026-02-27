import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.tracking_repository import create_tracking_update
from app.repositories.shipment_repository import (
    create_shipment,
    get_shipment_by_tracking_number,
    get_shipment_by_id,
    get_all_shipments_by_customer,
    update_shipment_status,
    assign_agent_to_shipment,
    delete_shipment
)
from app.repositories.tracking_repository import get_latest_tracking
from app.repositories.user_repository import get_user_by_id
from app.utils.constants import SHIPMENT_STATUSES


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


def update_status_service(db: Session, shipment_id, data: dict, current_user):
    shipment = get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if str(shipment.agent_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not assigned to this shipment")

    if data["status"] not in SHIPMENT_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {SHIPMENT_STATUSES}")

    updated = update_shipment_status(db, shipment, data["status"])

    # Auto-create tracking record on status update
    create_tracking_update(db, {
        "shipment_id": shipment_id,
        "location": data["location"],
        "status": data["status"]
    })

    return updated


def get_my_shipments(db: Session, customer_id):
    return get_all_shipments_by_customer(db, customer_id)


def update_status_service(db: Session, shipment_id, data: dict, current_user):
    shipment = get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    if str(shipment.agent_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not assigned to this shipment")

    if data["status"] not in SHIPMENT_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Choose from: {SHIPMENT_STATUSES}")

    return update_shipment_status(db, shipment, data["status"])


def assign_agent_service(db: Session, shipment_id, agent_id, current_user):
    shipment = get_shipment_by_id(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")

    agent = get_user_by_id(db, agent_id)
    if not agent or agent.role != "agent":
        raise HTTPException(status_code=400, detail="Invalid agent ID or user is not an agent")

    return assign_agent_to_shipment(db, shipment, agent_id)


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

