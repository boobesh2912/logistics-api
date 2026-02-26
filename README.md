# Logistics & Shipment Tracking API

FastAPI + PostgreSQL + JWT | Capstone Project - Hexaware Training

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

## Configure .env

```
DATABASE_URL=postgresql://sa:admin123@localhost:5432/logistics_db
SECRET_KEY=supersecretkey_logistics_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Run

```bash
uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs

## Test

```bash
pytest -v
```

## Sprint 1 Endpoints

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | /auth/register | Public | Register customer or agent |
| POST | /auth/login | Public | Login and get JWT token |
| POST | /shipments/ | Customer | Create new shipment |
| GET | /shipments/ | Customer | View all my shipments |
| GET | /shipments/{tracking_number} | Any Auth | Track shipment |
| DELETE | /shipments/{id} | Customer | Cancel shipment |
| POST | /tracking/{shipment_id} | Agent | Add tracking update |