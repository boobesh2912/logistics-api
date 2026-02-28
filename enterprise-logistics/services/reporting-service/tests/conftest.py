# tests/conftest.py — reporting-service
import uuid as uuid_lib
from datetime import datetime, timedelta

import pytest
from jose import jwt
from sqlalchemy import create_engine, types as satypes
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


# --- SQLite UUID compatibility shim ---
class _SQLiteUUID(satypes.TypeDecorator):
    impl = satypes.String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return str(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return uuid_lib.UUID(value) if value is not None else None


postgresql.UUID = lambda as_uuid=False: _SQLiteUUID()

# --- App imports (after patch) ---
from app.main import app  # noqa: E402
from app.core.database import get_shipment_db, get_auth_db  # noqa: E402
# Reporting models each declare their own Base — import both separately
from app.models.shipment import Base as ShipmentBase, Shipment  # noqa: E402
from app.models.user import Base as UserBase, User  # noqa: E402

SECRET_KEY = "supersecretkey_logistics_2026"
ALGORITHM = "HS256"

shipment_engine = create_engine(
    "sqlite:///./test_report_shipment.db",
    connect_args={"check_same_thread": False},
)
auth_engine = create_engine(
    "sqlite:///./test_report_auth.db",
    connect_args={"check_same_thread": False},
)

ShipmentTestSession = sessionmaker(autocommit=False, autoflush=False, bind=shipment_engine)
AuthTestSession = sessionmaker(autocommit=False, autoflush=False, bind=auth_engine)


def override_get_shipment_db():
    db = ShipmentTestSession()
    try:
        yield db
    finally:
        db.close()


def override_get_auth_db():
    db = AuthTestSession()
    try:
        yield db
    finally:
        db.close()


def make_token(role: str, uid: str = None) -> str:
    uid = uid or str(uuid_lib.uuid4())
    payload = {
        "sub": f"{role}@test.com",
        "role": role,
        "uid": uid,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture(autouse=True)
def setup_db():
    ShipmentBase.metadata.create_all(bind=shipment_engine)
    UserBase.metadata.create_all(bind=auth_engine)
    yield
    ShipmentBase.metadata.drop_all(bind=shipment_engine)
    UserBase.metadata.drop_all(bind=auth_engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_shipment_db] = override_get_shipment_db
    app.dependency_overrides[get_auth_db] = override_get_auth_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    return make_token("admin")


@pytest.fixture
def customer_token():
    return make_token("customer")


@pytest.fixture
def shipment_session():
    """Direct DB session for seeding test shipment data."""
    db = ShipmentTestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def auth_session():
    """Direct DB session for seeding test user data."""
    db = AuthTestSession()
    try:
        yield db
    finally:
        db.close()
