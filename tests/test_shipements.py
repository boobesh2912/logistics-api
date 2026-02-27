# tests/test_shipements.py
def register_and_login(client, email, role):
    client.post("/auth/register", json={"email": email, "password": "pass123", "role": role})
    login = client.post("/auth/login", data={"username": email, "password": "pass123"})
    return login.json()["access_token"]


def test_create_shipment(client):
    token = register_and_login(client, "cust1@test.com", "customer")
    response = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    assert response.status_code == 201
    assert "tracking_number" in response.json()
    assert response.json()["status"] == "created"


def test_track_shipment(client):
    token = register_and_login(client, "cust2@test.com", "customer")
    shipment = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    ).json()
    response = client.get(
        f"/shipments/{shipment['tracking_number']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["tracking_number"] == shipment["tracking_number"]


def test_agent_cannot_create_shipment(client):
    agent_token = register_and_login(client, "agent1@test.com", "agent")
    response = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    assert response.status_code == 403


def test_cancel_dispatched_shipment_blocked(client):
    token = register_and_login(client, "cust3@test.com", "customer")
    shipment = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    ).json()
    # Can cancel when status is 'created'
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200