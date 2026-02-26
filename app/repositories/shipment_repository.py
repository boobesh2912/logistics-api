from sqlalchemy.orm import Session
from app.models.shipment import Shipment


def create_shipment(db: Session, shipment_data: dict) -> Shipment:
    shipment = Shipment(**shipment_data)
    db.add(shipment)
    db.commit()
    db.refresh(shipment)
    return shipment


def get_shipment_by_tracking_number(db: Session, tracking_number: str) -> Shipment | None:
    return db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()


def get_shipment_by_id(db: Session, shipment_id) -> Shipment | None:
    return db.query(Shipment).filter(Shipment.id == shipment_id).first()


def get_all_shipments_by_customer(db: Session, customer_id):
    return db.query(Shipment).filter(Shipment.customer_id == customer_id).all()


def delete_shipment(db: Session, shipment: Shipment):
    db.delete(shipment)
    db.commit()