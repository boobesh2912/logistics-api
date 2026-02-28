# Logistics & Shipment Tracking API

A production-grade RESTful API for a Logistics & Shipment Tracking System built with FastAPI, PostgreSQL, and JWT Authentication.

> Capstone Project — Hexaware Training

---

## Overview

This system allows:
- **Customers** to create shipments and track deliveries
- **Delivery Agents** to update shipment status and add tracking updates
- **Admins** to manage hubs, users, and monitor performance

Similar to platforms like FedEx, Delhivery, or DHL backend systems.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| PostgreSQL | Primary database |
| JWT (python-jose) | Authentication |
| Passlib + bcrypt | Password hashing |
| Alembic | Database migrations |
| Docker | Containerization |
| Redis | Tracking cache & real-time status (Sprint 4 — architecture defined) |
| pytest + httpx | Testing |
| Python 3.11 | Runtime |

---

## Project Structure

### Sprint 1–3 (Monolith)

```
logistics-api/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── models/
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── shipment.py
│   │   ├── tracking.py
│   │   └── hub.py
│   ├── schemas/
│   │   ├── auth_schema.py
│   │   ├── shipment_schema.py
│   │   ├── tracking_schema.py
│   │   ├── hub_schema.py
│   │   └── user_schema.py
│   ├── repositories/
│   │   ├── user_repository.py
│   │   ├── shipment_repository.py
│   │   ├── tracking_repository.py
│   │   └── hub_repository.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── shipment_service.py
│   │   ├── tracking_service.py
│   │   └── hub_service.py
│   ├── api/
│   │   ├── router.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── shipments.py
│   │       ├── tracking.py
│   │       └── admin.py
│   ├── middleware/
│   │   ├── cors.py
│   │   ├── logging_middleware.py
│   │   └── rate_limiter.py
│   ├── exceptions/
│   │   ├── custom_exceptions.py
│   │   └── exception_handlers.py
│   └── utils/
│       ├── constants.py
│       └── validators.py
├── alembic/
├── alembic.ini
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_shipments.py
│   ├── test_tracking.py
│   ├── test_hubs.py
│   └── test_admin.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

### Sprint 4 (Enterprise Microservices)

```
enterprise-logistics/
├── services/
│   ├── auth-service/        -> Port 8001
│   ├── shipment-service/    -> Port 8002
│   ├── hub-service/         -> Port 8003
│   ├── tracking-service/    -> Port 8004
│   └── reporting-service/   -> Port 8005
├── docker-compose.yml
├── init-db.sql
└── .env
```

---

## Setup (Sprint 1–3 Monolith)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd logistics-api
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory:

```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/logistics_db
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> Note: Create the PostgreSQL database `logistics_db` before running the app.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Swagger UI: http://localhost:8000/docs

---

## API Endpoints

### Sprint 1 — Authentication & Shipment Creation

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | Public | Register as customer, agent, or admin |
| POST | `/auth/login` | Public | Login and receive JWT token |
| POST | `/shipments/` | Customer | Create new shipment |
| GET | `/shipments/` | Customer | View all my shipments |
| GET | `/shipments/{tracking_number}` | Any Auth | Track shipment by tracking number |

### Sprint 2 — Role-Based Updates & Agent Flow

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| PUT | `/shipments/{id}/status` | Agent | Update shipment status and location |
| POST | `/tracking/{shipment_id}` | Agent | Add tracking update |
| DELETE | `/shipments/{id}` | Customer | Cancel shipment (only if not dispatched) |
| PUT | `/shipments/{id}/assign-agent` | Admin | Assign delivery agent to shipment |

### Sprint 3 — Admin & Hub Management

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| GET | `/admin/hubs` | Admin | List all hubs |
| POST | `/admin/hubs` | Admin | Create a new hub |
| PUT | `/admin/hubs/{id}` | Admin | Update hub details |
| DELETE | `/admin/hubs/{id}` | Admin | Delete a hub |
| GET | `/admin/users` | Admin | View all registered users |
| DELETE | `/admin/users/{id}` | Admin | Delete a user |
| GET | `/admin/reports` | Admin | Get daily shipment reports |

---

## Database Tables

| Table | Key Columns |
|---|---|
| `users` | id (UUID), email, password_hash, role (customer/agent/admin) |
| `shipments` | id, tracking_number, customer_id, agent_id, status, source_address, destination_address, created_at |
| `tracking_updates` | id, shipment_id, location, status, updated_at |
| `hubs` | id, hub_name, city |

---

## Running Tests

```bash
pytest tests/ -v
```

29 tests — all passing.

---

## Sprint 4 — Enterprise Microservices

Each service is an independent FastAPI application with its own database and Docker container.

### Service & Port Layout

| Service | Port | Swagger UI | Database |
|---|---|---|---|
| auth-service | 8001 | http://localhost:8001/docs | auth_db |
| shipment-service | 8002 | http://localhost:8002/docs | shipment_db |
| hub-service | 8003 | http://localhost:8003/docs | hub_db |
| tracking-service | 8004 | http://localhost:8004/docs | tracking_db |
| reporting-service | 8005 | http://localhost:8005/docs | reads shipment_db + auth_db |

### Enterprise Architecture

| Communication | Technology |
|---|---|
| Client → Service | REST (HTTP) |
| Service → Service | Kafka (architecture defined in PDF; REST fallback used for demo) |
| Real-time tracking | Redis (architecture defined in PDF) |
| Persistence | PostgreSQL |
| Deployment | Docker |

### Run with Docker

```bash
cd enterprise-logistics
docker-compose up --build
```

This command:
- Builds **5 separate Docker images** (one per service)
- Pulls `postgres:15` from Docker Hub
- Starts **6 containers** in total (postgres + 5 services)
- Creates all required databases automatically via `init-db.sql`
- Each service runs on its own port with its own Swagger UI

### Enterprise .env

Create `enterprise-logistics/.env`:

```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=postgres
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## Author

Developed by **Boobesh AG** | Hexaware Capstone Project
