from fastapi import APIRouter
from app.api.routes import auth, shipments, tracking

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(shipments.router)
api_router.include_router(tracking.router)