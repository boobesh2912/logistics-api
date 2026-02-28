from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import user  # noqa
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service", version="1.0.0")

app.include_router(auth_router)


@app.get("/health")
def health():
    return {"service": "auth-service", "status": "healthy"}
