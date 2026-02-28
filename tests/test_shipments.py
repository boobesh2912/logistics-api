# tests/test_shipments.py
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


def test_cancel_shipment(client):
    token = register_and_login(client, "cust3@test.com", "customer")
    shipment = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    ).json()
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_cancel_dispatched_shipment_blocked(client):
    admin_token = register_and_login(client, "admin3@test.com", "admin")
    customer_token = register_and_login(client, "cust4@test.com", "customer")
    agent_token = register_and_login(client, "agent3@test.com", "agent")

    shipment = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    ).json()

    # Admin assigns agent
    users = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    agent = next(u for u in users if u["email"] == "agent3@test.com")
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent["id"]}
    )

    # Agent updates status to in_transit
    client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem Hub"}
    )

    # Customer tries to cancel — must be blocked
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    assert response.status_code == 400