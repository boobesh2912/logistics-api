# tests/test_auth.py — auth-service
"""
Comprehensive tests for the Auth Service.
Covers: registration, login, JWT validation, role enforcement, error cases.
"""
from jose import jwt


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    response = client.get("/health")
    body = response.json()
    assert body["service"] == "auth-service"
    assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Registration — Happy Path
# ---------------------------------------------------------------------------

def test_register_customer_returns_201(client):
    response = client.post("/auth/register", json={
        "email": "customer@test.com",
        "password": "pass123",
        "role": "customer"
    })
    assert response.status_code == 201


def test_register_customer_response_contains_id_email_role(client):
    response = client.post("/auth/register", json={
        "email": "customer@test.com",
        "password": "pass123",
        "role": "customer"
    })
    body = response.json()
    assert "id" in body
    assert body["email"] == "customer@test.com"
    assert body["role"] == "customer"


def test_register_agent_role_is_accepted(client):
    response = client.post("/auth/register", json={
        "email": "agent@test.com",
        "password": "pass123",
        "role": "agent"
    })
    assert response.status_code == 201
    assert response.json()["role"] == "agent"


def test_register_admin_role_is_accepted(client):
    response = client.post("/auth/register", json={
        "email": "admin@test.com",
        "password": "pass123",
        "role": "admin"
    })
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


def test_register_response_does_not_expose_password_hash(client):
    response = client.post("/auth/register", json={
        "email": "secure@test.com",
        "password": "mysecretpassword",
        "role": "customer"
    })
    body = response.json()
    assert "password" not in body
    assert "password_hash" not in body


def test_register_id_is_a_valid_uuid_string(client):
    import uuid
    response = client.post("/auth/register", json={
        "email": "uuid@test.com",
        "password": "pass123",
        "role": "customer"
    })
    returned_id = response.json()["id"]
    uuid.UUID(returned_id)  # raises ValueError if not valid UUID


# ---------------------------------------------------------------------------
# Registration — Error Cases
# ---------------------------------------------------------------------------

def test_register_duplicate_email_returns_400(client):
    payload = {"email": "dup@test.com", "password": "pass123", "role": "customer"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400


def test_register_duplicate_email_error_message(client):
    payload = {"email": "dup2@test.com", "password": "pass123", "role": "customer"}
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_role_returns_400(client):
    response = client.post("/auth/register", json={
        "email": "badrole@test.com",
        "password": "pass123",
        "role": "superuser"
    })
    assert response.status_code == 400


def test_register_invalid_role_error_message(client):
    response = client.post("/auth/register", json={
        "email": "badrole2@test.com",
        "password": "pass123",
        "role": "superuser"
    })
    assert "invalid role" in response.json()["detail"].lower()


def test_register_invalid_email_format_returns_422(client):
    response = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "pass123",
        "role": "customer"
    })
    assert response.status_code == 422


def test_register_missing_email_returns_422(client):
    response = client.post("/auth/register", json={
        "password": "pass123",
        "role": "customer"
    })
    assert response.status_code == 422


def test_register_missing_password_returns_422(client):
    response = client.post("/auth/register", json={
        "email": "test@test.com",
        "role": "customer"
    })
    assert response.status_code == 422


def test_register_missing_role_returns_422(client):
    response = client.post("/auth/register", json={
        "email": "test@test.com",
        "password": "pass123"
    })
    assert response.status_code == 422


def test_register_empty_body_returns_422(client):
    response = client.post("/auth/register", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login — Happy Path
# ---------------------------------------------------------------------------

def test_login_returns_200(client):
    client.post("/auth/register", json={
        "email": "login@test.com", "password": "pass123", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "login@test.com", "password": "pass123"
    })
    assert response.status_code == 200


def test_login_response_contains_access_token(client):
    client.post("/auth/register", json={
        "email": "token@test.com", "password": "pass123", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "token@test.com", "password": "pass123"
    })
    assert "access_token" in response.json()


def test_login_token_type_is_bearer(client):
    client.post("/auth/register", json={
        "email": "bearer@test.com", "password": "pass123", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "bearer@test.com", "password": "pass123"
    })
    assert response.json()["token_type"] == "bearer"


def test_login_token_contains_required_claims(client):
    """JWT must contain sub (email), role, uid, and exp claims."""
    client.post("/auth/register", json={
        "email": "claims@test.com", "password": "pass123", "role": "agent"
    })
    response = client.post("/auth/login", data={
        "username": "claims@test.com", "password": "pass123"
    })
    token = response.json()["access_token"]
    payload = jwt.decode(
        token,
        "supersecretkey_logistics_2026",
        algorithms=["HS256"]
    )
    assert payload["sub"] == "claims@test.com"
    assert payload["role"] == "agent"
    assert "uid" in payload
    assert "exp" in payload


def test_login_token_uid_matches_registered_user_id(client):
    """The uid in the JWT must match the id returned at registration."""
    reg_response = client.post("/auth/register", json={
        "email": "uid@test.com", "password": "pass123", "role": "customer"
    })
    user_id = reg_response.json()["id"]

    login_response = client.post("/auth/login", data={
        "username": "uid@test.com", "password": "pass123"
    })
    token = login_response.json()["access_token"]
    payload = jwt.decode(
        token,
        "supersecretkey_logistics_2026",
        algorithms=["HS256"]
    )
    assert payload["uid"] == user_id


# ---------------------------------------------------------------------------
# Login — Error Cases
# ---------------------------------------------------------------------------

def test_login_wrong_password_returns_401(client):
    client.post("/auth/register", json={
        "email": "wrongpwd@test.com", "password": "correct", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "wrongpwd@test.com", "password": "wrong"
    })
    assert response.status_code == 401


def test_login_wrong_password_error_message(client):
    client.post("/auth/register", json={
        "email": "wrongpwd2@test.com", "password": "correct", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "wrongpwd2@test.com", "password": "wrong"
    })
    assert "invalid credentials" in response.json()["detail"].lower()


def test_login_nonexistent_email_returns_401(client):
    response = client.post("/auth/login", data={
        "username": "ghost@test.com", "password": "pass123"
    })
    assert response.status_code == 401


def test_login_missing_credentials_returns_422(client):
    response = client.post("/auth/login", data={})
    assert response.status_code == 422


def test_login_empty_password_returns_401(client):
    client.post("/auth/register", json={
        "email": "emptypwd@test.com", "password": "realpass", "role": "customer"
    })
    response = client.post("/auth/login", data={
        "username": "emptypwd@test.com", "password": ""
    })
    assert response.status_code == 401
