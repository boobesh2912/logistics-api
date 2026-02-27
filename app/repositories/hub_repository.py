from sqlalchemy.orm import Session
from app.models.hub import Hub
from uuid import UUID


def create_hub(db: Session, data: dict) -> Hub:
    hub = Hub(**data)
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


def get_hub_by_id(db: Session, hub_id) -> Hub | None:
    if isinstance(hub_id, str):
        hub_id = UUID(hub_id)
    return db.query(Hub).filter(Hub.id == hub_id).first()


def get_all_hubs(db: Session):
    return db.query(Hub).all()


def update_hub(db: Session, hub: Hub, data: dict) -> Hub:
    for key, value in data.items():
        if value is not None:
            setattr(hub, key, value)
    db.commit()
    db.refresh(hub)
    return hub


def delete_hub(db: Session, hub: Hub):
    db.delete(hub)
    db.commit()