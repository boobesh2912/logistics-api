from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import register_user, login_user
from app.schemas.auth_schema import RegisterRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(user: RegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, user.dict())


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    return login_user(db, {"email": form_data.username, "password": form_data.password})