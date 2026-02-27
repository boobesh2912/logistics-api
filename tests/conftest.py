import pytest
from fastapi.testclient import TestClient
from app.main import app   # change if your path is different


@pytest.fixture
def client():
    return TestClient(app)