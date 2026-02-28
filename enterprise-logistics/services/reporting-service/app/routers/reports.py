from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date
from typing import List
from uuid import UUID
from app.core.database import get_shipment_db, get_auth_db
from app.dependencies import require_role
from app.models.shipment import Shipment
from app.models.user import User
from app.schemas.report_schema import ReportResponse, UserResponse

router = APIRouter(tags=["Reporting"])


@router.get("/reports", response_model=ReportResponse)
def get_reports(
    shipment_db: Session = Depends(get_shipment_db),
    current_user: dict = Depends(require_role("admin"))
):
    today = date.today()
    total_today = shipment_db.query(Shipment).filter(
        cast(Shipment.created_at, Date) == today
    ).count()
    delivered = shipment_db.query(Shipment).filter(Shipment.status == "delivered").count()
    in_transit = shipment_db.query(Shipment).filter(Shipment.status == "in_transit").count()
    return {"total_shipments_today": total_today, "delivered": delivered, "in_transit": in_transit}


@router.get("/admin/users", response_model=List[UserResponse])
def get_all_users(
    auth_db: Session = Depends(get_auth_db),
    current_user: dict = Depends(require_role("admin"))
):
    return auth_db.query(User).all()


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: UUID,
    auth_db: Session = Depends(get_auth_db),
    current_user: dict = Depends(require_role("admin"))
):
    user = auth_db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    auth_db.delete(user)
    auth_db.commit()
    return {"message": "User deleted successfully"}
