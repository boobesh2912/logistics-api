def get_customer_token(client):
    client.post("/auth/register", json={"email": "customer@test.com", "password": "pass123", "role": "customer"})
    login = client.post("/auth/login", data={"username": "customer@test.com", "password": "pass123"})
    return login.json()["access_token"]


def get_agent_token(client):
    client.post("/auth/register", json={"email": "agent@test.com", "password": "pass123", "role": "agent"})
    login = client.post("/auth/login", data={"username": "agent@test.com", "password": "pass123"})
    return login.json()["access_token"]


def get_admin_token(client):
    client.post("/auth/register", json={"email": "admin@test.com", "password": "pass123", "role": "admin"})
    login = client.post("/auth/login", data={"username": "admin@test.com", "password": "pass123"})
    return login.json()["access_token"]


def get_agent_id(client, agent_token):
    # Register agent and get their ID via token decode (we get it from DB via shipment assign)
    client.post("/auth/register", json={"email": "agent2@test.com", "password": "pass123", "role": "agent"})
    login = client.post("/auth/login", data={"username": "agent2@test.com", "password": "pass123"})
    return login.json()


def test_customer_can_view_all_shipments(client):
    customer_token = get_customer_token(client)
    client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    response = client.get("/shipments/", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_customer_can_cancel_shipment(client):
    customer_token = get_customer_token(client)
    create = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    shipment_id = create.json()["id"]
    response = client.delete(f"/shipments/{shipment_id}", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 200


def test_agent_cannot_update_unassigned_shipment(client):
    customer_token = get_customer_token(client)
    agent_token = get_agent_token(client)

    create = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    shipment_id = create.json()["id"]

    response = client.put(
        f"/shipments/{shipment_id}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem Hub"}
    )
    assert response.status_code == 403


def test_customer_cannot_update_status(client):
    customer_token = get_customer_token(client)
    create = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    shipment_id = create.json()["id"]

    response = client.put(
        f"/shipments/{shipment_id}/status",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"status": "in_transit", "location": "Salem Hub"}
    )
    assert response.status_code == 403