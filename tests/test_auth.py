# tests/test_auth.py
def test_register_customer(client):
    response = client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "pass123",
        "role": "customer"
    })
    assert response.status_code == 201


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123", "role": "customer"})
    response = client.post("/auth/register", json={"email": "dup@test.com", "password": "pass123", "role": "customer"})
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "login@test.com", "password": "pass123", "role": "customer"})
    response = client.post("/auth/login", data={"username": "login@test.com", "password": "pass123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", data={"username": "wrong@test.com", "password": "wrong"})
    assert response.status_code == 401


def test_register_invalid_role(client):
    response = client.post("/auth/register", json={"email": "x@test.com", "password": "pass123", "role": "superuser"})
    assert response.status_code == 400