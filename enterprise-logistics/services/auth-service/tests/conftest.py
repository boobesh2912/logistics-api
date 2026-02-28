# tests/conftest.py — auth-service
import uuid as uuid_lib

import pytest
from sqlalchemy import create_engine, types as satypes
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient


# --- SQLite UUID compatibility shim ---
# Must patch BEFORE any app module is imported so that
# sqlalchemy.dialects.postgresql.UUID resolves to a SQLite-safe String(36).
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
from app.core.database import Base, get_db  # noqa: E402

SQLITE_TEST_URL = "sqlite:///./test_auth_svc.db"
engine = create_engine(SQLITE_TEST_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
