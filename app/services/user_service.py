from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import get_user_by_id, get_user_by_email


def get_user_profile(db: Session, user_id):
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_email_service(db: Session, email: str):
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user