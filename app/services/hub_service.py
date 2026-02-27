from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from app.repositories.hub_repository import (
    create_hub, get_hub_by_id, update_hub, delete_hub, get_all_hubs
)
from app.repositories.user_repository import get_user_by_id
from app.models.user import User
from app.models.shipment import Shipment


def create_hub_service(db: Session, data: dict):
    return create_hub(db, data)


def get_all_hubs_service(db: Session):
    return get_all_hubs(db)


def update_hub_service(db: Session, hub_id, data: dict):
    hub = get_hub_by_id(db, hub_id)
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    return update_hub(db, hub, data)


def delete_hub_service(db: Session, hub_id):
    hub = get_hub_by_id(db, hub_id)
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    delete_hub(db, hub)
    return {"message": "Hub deleted successfully"}


def get_all_users_service(db: Session):
    return db.query(User).all()


def delete_user_service(db: Session, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


def get_reports_service(db: Session):
    # Fixed: use func.date() to compare properly in PostgreSQL
    today = func.current_date()
    total_today = db.query(Shipment).filter(
        func.date(Shipment.created_at) == today
    ).count()
    delivered = db.query(Shipment).filter(
        Shipment.status == "delivered"
    ).count()
    in_transit = db.query(Shipment).filter(
        Shipment.status == "in_transit"
    ).count()
    return {
        "total_shipments_today": total_today,
        "delivered": delivered,
        "in_transit": in_transit
    }