from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.repositories.user_repository import create_user, get_user_by_email
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data: dict):
    existing = get_user_by_email(db, data["email"])
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    if data["role"] not in ["customer", "agent", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Choose: customer, agent, admin")

    data["password_hash"] = hash_password(data.pop("password"))
    return create_user(db, data)


def login_user(db: Session, data: dict):
    user = get_user_by_email(db, data["email"])
    if not user or not verify_password(data["password"], user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}