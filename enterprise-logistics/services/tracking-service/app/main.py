from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import tracking  # noqa
from app.routers.tracking import router as tracking_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tracking Service", version="1.0.0")

app.include_router(tracking_router)


@app.get("/health")
def health():
    return {"service": "tracking-service", "status": "healthy"}
