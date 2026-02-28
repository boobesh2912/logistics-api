from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import shipment  # noqa
from app.routers.shipments import router as shipment_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shipment Service", version="1.0.0")

app.include_router(shipment_router)


@app.get("/health")
def health():
    return {"service": "shipment-service", "status": "healthy"}
