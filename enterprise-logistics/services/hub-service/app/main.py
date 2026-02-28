from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import hub  # noqa
from app.routers.hubs import router as hub_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hub Service", version="1.0.0")

app.include_router(hub_router)


@app.get("/health")
def health():
    return {"service": "hub-service", "status": "healthy"}
