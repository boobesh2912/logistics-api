# tests/test_hubs.py — hub-service
"""
Comprehensive tests for the Hub Service.
Covers: CRUD operations, admin-only access, partial updates, error cases.
"""
import uuid as uuid_lib


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_hub(client, token, hub_name="Mumbai Hub", city="Mumbai"):
    return client.post(
        "/admin/hubs/",
        headers={"Authorization": f"Bearer {token}"},
        json={"hub_name": hub_name, "city": city},
    )


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    body = client.get("/health").json()
    assert body["service"] == "hub-service"
    assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Create Hub — Happy Path
# ---------------------------------------------------------------------------

def test_create_hub_as_admin_returns_201(client, admin_token):
    response = create_hub(client, admin_token)
    assert response.status_code == 201


def test_create_hub_response_contains_id_hub_name_city(client, admin_token):
    body = create_hub(client, admin_token, "Delhi Hub", "Delhi").json()
    assert "id" in body
    assert body["hub_name"] == "Delhi Hub"
    assert body["city"] == "Delhi"


def test_create_hub_id_is_valid_uuid(client, admin_token):
    import uuid
    body = create_hub(client, admin_token).json()
    uuid.UUID(body["id"])  # raises ValueError if not valid


def test_create_multiple_hubs(client, admin_token):
    create_hub(client, admin_token, "Hub A", "City A")
    create_hub(client, admin_token, "Hub B", "City B")
    response = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {admin_token}"})
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# Create Hub — Role Enforcement
# ---------------------------------------------------------------------------

def test_create_hub_as_customer_returns_403(client, customer_token):
    response = create_hub(client, customer_token)
    assert response.status_code == 403


def test_create_hub_as_agent_returns_403(client, agent_token):
    response = create_hub(client, agent_token)
    assert response.status_code == 403


def test_create_hub_without_auth_returns_401(client):
    response = client.post("/admin/hubs/", json={"hub_name": "Test", "city": "Test"})
    assert response.status_code == 401


def test_create_hub_with_invalid_token_returns_401(client):
    response = client.post(
        "/admin/hubs/",
        headers={"Authorization": "Bearer bad.token.here"},
        json={"hub_name": "Test", "city": "Test"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create Hub — Validation
# ---------------------------------------------------------------------------

def test_create_hub_missing_hub_name_returns_422(client, admin_token):
    response = client.post(
        "/admin/hubs/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"city": "Mumbai"},
    )
    assert response.status_code == 422


def test_create_hub_missing_city_returns_422(client, admin_token):
    response = client.post(
        "/admin/hubs/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Mumbai Hub"},
    )
    assert response.status_code == 422


def test_create_hub_empty_body_returns_422(client, admin_token):
    response = client.post(
        "/admin/hubs/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# List Hubs
# ---------------------------------------------------------------------------

def test_list_hubs_returns_empty_list_when_no_hubs(client, admin_token):
    response = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_hubs_returns_all_created_hubs(client, admin_token):
    create_hub(client, admin_token, "Hub 1", "City 1")
    create_hub(client, admin_token, "Hub 2", "City 2")
    create_hub(client, admin_token, "Hub 3", "City 3")
    response = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_list_hubs_response_items_have_correct_fields(client, admin_token):
    create_hub(client, admin_token, "Chennai Hub", "Chennai")
    items = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert "id" in items[0]
    assert "hub_name" in items[0]
    assert "city" in items[0]


def test_list_hubs_as_customer_returns_403(client, customer_token):
    response = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 403


def test_list_hubs_as_agent_returns_403(client, agent_token):
    response = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {agent_token}"})
    assert response.status_code == 403


def test_list_hubs_without_auth_returns_401(client):
    response = client.get("/admin/hubs/")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Update Hub
# ---------------------------------------------------------------------------

def test_update_hub_name_as_admin_returns_200(client, admin_token):
    hub = create_hub(client, admin_token, "Old Name", "Mumbai").json()
    response = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "New Name"},
    )
    assert response.status_code == 200


def test_update_hub_name_is_persisted(client, admin_token):
    hub = create_hub(client, admin_token, "Old Name", "Mumbai").json()
    body = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "New Name"},
    ).json()
    assert body["hub_name"] == "New Name"


def test_update_hub_name_does_not_change_city(client, admin_token):
    hub = create_hub(client, admin_token, "Hub A", "Original City").json()
    body = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "Hub B"},
    ).json()
    assert body["city"] == "Original City"


def test_update_hub_city_does_not_change_hub_name(client, admin_token):
    hub = create_hub(client, admin_token, "Original Name", "Old City").json()
    body = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"city": "New City"},
    ).json()
    assert body["hub_name"] == "Original Name"
    assert body["city"] == "New City"


def test_update_hub_both_fields_simultaneously(client, admin_token):
    hub = create_hub(client, admin_token, "A", "B").json()
    body = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "X", "city": "Y"},
    ).json()
    assert body["hub_name"] == "X"
    assert body["city"] == "Y"


def test_update_nonexistent_hub_returns_404(client, admin_token):
    fake_id = str(uuid_lib.uuid4())
    response = client.put(
        f"/admin/hubs/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "X"},
    )
    assert response.status_code == 404


def test_update_nonexistent_hub_error_message(client, admin_token):
    fake_id = str(uuid_lib.uuid4())
    body = client.put(
        f"/admin/hubs/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"hub_name": "X"},
    ).json()
    assert "not found" in body["detail"].lower()


def test_update_hub_as_customer_returns_403(client, admin_token, customer_token):
    hub = create_hub(client, admin_token).json()
    response = client.put(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"hub_name": "X"},
    )
    assert response.status_code == 403


def test_update_hub_without_auth_returns_401(client, admin_token):
    hub = create_hub(client, admin_token).json()
    response = client.put(f"/admin/hubs/{hub['id']}", json={"hub_name": "X"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Delete Hub
# ---------------------------------------------------------------------------

def test_delete_hub_as_admin_returns_200(client, admin_token):
    hub = create_hub(client, admin_token).json()
    response = client.delete(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


def test_delete_hub_returns_success_message(client, admin_token):
    hub = create_hub(client, admin_token).json()
    body = client.delete(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    assert "deleted" in body["message"].lower()


def test_deleted_hub_no_longer_appears_in_list(client, admin_token):
    hub = create_hub(client, admin_token, "ToDelete", "City").json()
    client.delete(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    hubs = client.get("/admin/hubs/", headers={"Authorization": f"Bearer {admin_token}"}).json()
    hub_ids = [h["id"] for h in hubs]
    assert hub["id"] not in hub_ids


def test_delete_nonexistent_hub_returns_404(client, admin_token):
    fake_id = str(uuid_lib.uuid4())
    response = client.delete(
        f"/admin/hubs/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_delete_hub_as_customer_returns_403(client, admin_token, customer_token):
    hub = create_hub(client, admin_token).json()
    response = client.delete(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 403


def test_delete_hub_as_agent_returns_403(client, admin_token, agent_token):
    hub = create_hub(client, admin_token).json()
    response = client.delete(
        f"/admin/hubs/{hub['id']}",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 403


def test_delete_hub_without_auth_returns_401(client, admin_token):
    hub = create_hub(client, admin_token).json()
    response = client.delete(f"/admin/hubs/{hub['id']}")
    assert response.status_code == 401
