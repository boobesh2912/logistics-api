def register_and_login(client, email, role):
    client.post("/auth/register", json={"email": email, "password": "pass123", "role": role})
    login = client.post("/auth/login", data={"username": email, "password": "pass123"})
    return login.json()["access_token"]


def test_admin_create_hub(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    response = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Chennai Hub", "city": "Chennai"}
    )
    assert response.status_code == 201
    assert response.json()["hub_name"] == "Chennai Hub"


def test_admin_update_hub(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    create = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Chennai Hub", "city": "Chennai"}
    )
    hub_id = create.json()["id"]
    response = client.put(
        f"/admin/hubs/{hub_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Chennai Central Hub", "city": "Chennai"}
    )
    assert response.status_code == 200
    assert response.json()["hub_name"] == "Chennai Central Hub"


def test_admin_delete_hub(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    create = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Chennai Hub", "city": "Chennai"}
    )
    hub_id = create.json()["id"]
    response = client.delete(
        f"/admin/hubs/{hub_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200


def test_admin_get_users(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    response = client.get(
        "/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_get_reports(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    response = client.get(
        "/admin/reports",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_shipments_today" in data
    assert "delivered" in data
    assert "in_transit" in data


def test_customer_cannot_access_admin(client):
    customer_token = register_and_login(client, "customer@test.com", "customer")
    response = client.post(
        "/admin/hubs",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"hub_name": "Chennai Hub", "city": "Chennai"}
    )
    assert response.status_code == 403


def test_admin_delete_user(client):
    admin_token = register_and_login(client, "admin@test.com", "admin")
    client.post("/auth/register", json={
        "email": "todelete@test.com", "password": "pass123", "role": "customer"
    })
    users = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    user_to_delete = next(u for u in users.json() if u["email"] == "todelete@test.com")
    response = client.delete(
        f"/admin/users/{user_to_delete['id']}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200