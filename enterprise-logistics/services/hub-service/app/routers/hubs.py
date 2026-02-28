from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.database import get_db
from app.dependencies import require_role
from app.models.hub import Hub
from app.schemas.hub_schema import HubCreate, HubUpdate, HubResponse

router = APIRouter(prefix="/admin/hubs", tags=["Hubs"])


@router.get("/", response_model=List[HubResponse])
def list_hubs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    return db.query(Hub).all()


@router.post("/", response_model=HubResponse, status_code=201)
def create_hub(
    data: HubCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    hub = Hub(hub_name=data.hub_name, city=data.city)
    db.add(hub)
    db.commit()
    db.refresh(hub)
    return hub


@router.put("/{hub_id}", response_model=HubResponse)
def update_hub(
    hub_id: UUID,
    data: HubUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    hub = db.query(Hub).filter(Hub.id == hub_id).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    if data.hub_name is not None:
        hub.hub_name = data.hub_name
    if data.city is not None:
        hub.city = data.city
    db.commit()
    db.refresh(hub)
    return hub


@router.delete("/{hub_id}")
def delete_hub(
    hub_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("admin"))
):
    hub = db.query(Hub).filter(Hub.id == hub_id).first()
    if not hub:
        raise HTTPException(status_code=404, detail="Hub not found")
    db.delete(hub)
    db.commit()
    return {"message": "Hub deleted successfully"}
