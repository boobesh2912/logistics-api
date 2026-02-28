from fastapi import FastAPI
from app.routers.reports import router as report_router

app = FastAPI(title="Reporting Service", version="1.0.0")

app.include_router(report_router)


@app.get("/health")
def health():
    return {"service": "reporting-service", "status": "healthy"}
