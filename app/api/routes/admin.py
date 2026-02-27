from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from app.core.database import get_db
from app.core.dependencies import require_role
from app.services.hub_service import (
    create_hub_service,
    update_hub_service,
    delete_hub_service,
    get_all_users_service,
    delete_user_service,
    get_reports_service
)
from app.schemas.hub_schema import HubCreate, HubUpdate, HubResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/hubs", response_model=HubResponse, status_code=201)
def create_hub(
    data: HubCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return create_hub_service(db, data.model_dump())


@router.put("/hubs/{hub_id}", response_model=HubResponse)
def update_hub(
    hub_id: UUID,
    data: HubUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return update_hub_service(db, hub_id, data.model_dump())


@router.delete("/hubs/{hub_id}")
def delete_hub(
    hub_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return delete_hub_service(db, hub_id)


@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return get_all_users_service(db)


@router.delete("/users/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return delete_user_service(db, user_id)


@router.get("/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin"))
):
    return get_reports_service(db)