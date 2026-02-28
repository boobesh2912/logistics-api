def register_and_login(client, email, role):
    client.post("/auth/register", json={"email": email, "password": "pass123", "role": role})
    login = client.post("/auth/login", data={"username": email, "password": "pass123"})
    return login.json()["access_token"]


def test_create_hub(client):
    admin_token = register_and_login(client, "admin@hub.com", "admin")
    response = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Mumbai Hub", "city": "Mumbai"}
    )
    assert response.status_code == 201
    assert response.json()["hub_name"] == "Mumbai Hub"
    assert response.json()["city"] == "Mumbai"


def test_list_hubs(client):
    admin_token = register_and_login(client, "admin@hub.com", "admin")
    client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Delhi Hub", "city": "Delhi"}
    )
    response = client.get("/admin/hubs", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) >= 1


def test_update_hub(client):
    admin_token = register_and_login(client, "admin@hub.com", "admin")
    create = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Old Hub", "city": "Pune"}
    )
    hub_id = create.json()["id"]
    response = client.put(
        f"/admin/hubs/{hub_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Updated Hub", "city": "Pune"}
    )
    assert response.status_code == 200
    assert response.json()["hub_name"] == "Updated Hub"


def test_delete_hub(client):
    admin_token = register_and_login(client, "admin@hub.com", "admin")
    create = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Temp Hub", "city": "Hyderabad"}
    )
    hub_id = create.json()["id"]
    response = client.delete(
        f"/admin/hubs/{hub_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Hub deleted successfully"


def test_customer_cannot_create_hub(client):
    customer_token = register_and_login(client, "customer@hub.com", "customer")
    response = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"hub_name": "Fake Hub", "city": "Chennai"}
    )
    assert response.status_code == 403


def test_delete_nonexistent_hub(client):
    admin_token = register_and_login(client, "admin@hub.com", "admin")
    response = client.delete(
        "/admin/hubs/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 404