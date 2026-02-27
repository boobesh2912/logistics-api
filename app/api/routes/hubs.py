from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_role
from app.services.hub_service import (
    create_hub_service,
    update_hub_service,
    delete_hub_service,
    get_all_hubs_service
)
from app.schemas.hub_schema import HubCreate, HubUpdate, HubResponse

router = APIRouter(prefix="/hubs", tags=["Hubs"])


@router.post("/", response_model=HubResponse, status_code=201)
def create_hub(
    data: HubCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return create_hub_service(db, data.model_dump())


@router.get("/", response_model=List[HubResponse])
def list_hubs(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return get_all_hubs_service(db)


@router.put("/{hub_id}", response_model=HubResponse)
def update_hub(
    hub_id: str,
    data: HubUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return update_hub_service(db, hub_id, data.model_dump())


@router.delete("/{hub_id}")
def delete_hub(
    hub_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return delete_hub_service(db, hub_id)