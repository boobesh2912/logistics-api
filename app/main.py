from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.database import engine, Base
from app.api.router import api_router
from app.middleware.cors import setup_cors
from app.middleware.logging_middleware import logging_middleware
from app.middleware.rate_limiter import rate_limit_middleware
from app.exceptions.custom_exceptions import (
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)

# Import models so SQLAlchemy registers them
from app.models import user, shipment, tracking, hub  # noqa

app = FastAPI(
    title="Logistics & Shipment Tracking API",
    description="Logistics & Shipment Tracking System | Sprints 1-3 | Hexaware Capstone",
    version="1.0.0"
)

# Create tables
Base.metadata.create_all(bind=engine)

# Middleware
setup_cors(app)
app.middleware("http")(logging_middleware)
app.middleware("http")(rate_limit_middleware)

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Logistics API is running", "status": "success"}


@app.get("/health")
def health():
    return {"status": "healthy"}