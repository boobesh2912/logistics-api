from fastapi import APIRouter
from app.api.routes import auth, shipments, tracking, admin

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(shipments.router)
api_router.include_router(tracking.router)
api_router.include_router(admin.router)