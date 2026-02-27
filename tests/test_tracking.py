def register_and_login(client, email, role):
    client.post("/auth/register", json={"email": email, "password": "pass123", "role": role})
    login = client.post("/auth/login", data={"username": email, "password": "pass123"})
    return login.json()["access_token"]


def create_shipment(client, token):
    response = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    )
    return response.json()


def test_customer_view_all_shipments(client):
    token = register_and_login(client, "customer@test.com", "customer")
    create_shipment(client, token)
    response = client.get("/shipments/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_customer_cancel_shipment(client):
    token = register_and_login(client, "customer@test.com", "customer")
    shipment = create_shipment(client, token)
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_agent_cannot_update_unassigned_shipment(client):
    customer_token = register_and_login(client, "customer@test.com", "customer")
    agent_token = register_and_login(client, "agent@test.com", "agent")
    shipment = create_shipment(client, customer_token)
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem Hub"}
    )
    assert response.status_code == 403


def test_customer_cannot_update_status(client):
    customer_token = register_and_login(client, "customer@test.com", "customer")
    shipment = create_shipment(client, customer_token)
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"status": "in_transit", "location": "Salem Hub"}
    )
    assert response.status_code == 403


def test_admin_assign_agent(client):
    admin_token = register_and_login(client, "admin2@test.com", "admin")
    customer_token = register_and_login(client, "customer2@test.com", "customer")
    client.post("/auth/register", json={"email": "agent2@test.com", "password": "pass123", "role": "agent"})

    shipment = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai", "destination_address": "Bangalore"}
    ).json()

    users = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    agent = next(u for u in users if u["email"] == "agent2@test.com")

    response = client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent["id"]}
    )
    assert response.status_code == 200