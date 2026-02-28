# tests/test_tracking.py — tracking-service
"""
Comprehensive tests for the Tracking Service.
Covers: adding updates, retrieving history, role enforcement, ordering, isolation.
"""
import uuid as uuid_lib
from conftest import make_token


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    body = client.get("/health").json()
    assert body["service"] == "tracking-service"
    assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Add Tracking Update — Happy Path
# ---------------------------------------------------------------------------

def test_add_tracking_update_as_agent_returns_201(client, agent_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Chennai Hub", "status": "in_transit"},
    )
    assert response.status_code == 201


def test_add_tracking_update_response_contains_required_fields(client, agent_token, sample_shipment_id):
    body = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Chennai Hub", "status": "in_transit"},
    ).json()
    assert "id" in body
    assert "shipment_id" in body
    assert "location" in body
    assert "status" in body
    assert "updated_at" in body


def test_add_tracking_update_response_has_correct_values(client, agent_token, sample_shipment_id):
    body = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Salem Hub", "status": "out_for_delivery"},
    ).json()
    assert body["location"] == "Salem Hub"
    assert body["status"] == "out_for_delivery"
    assert body["shipment_id"] == sample_shipment_id


def test_add_multiple_tracking_updates_for_same_shipment(client, agent_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Stop 1", "status": "in_transit"},
    )
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Stop 2", "status": "out_for_delivery"},
    )
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# Add Tracking Update — Role Enforcement
# ---------------------------------------------------------------------------

def test_add_tracking_update_as_customer_returns_403(client, customer_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    assert response.status_code == 403


def test_add_tracking_update_as_admin_returns_403(client, admin_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    assert response.status_code == 403


def test_add_tracking_update_without_auth_returns_401(client, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        json={"location": "Hub", "status": "in_transit"},
    )
    assert response.status_code == 401


def test_add_tracking_update_with_invalid_token_returns_401(client, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": "Bearer invalid.token.here"},
        json={"location": "Hub", "status": "in_transit"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Add Tracking Update — Validation
# ---------------------------------------------------------------------------

def test_add_tracking_update_missing_location_returns_422(client, agent_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit"},
    )
    assert response.status_code == 422


def test_add_tracking_update_missing_status_returns_422(client, agent_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub"},
    )
    assert response.status_code == 422


def test_add_tracking_update_empty_body_returns_422(client, agent_token, sample_shipment_id):
    response = client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Get Tracking History — Happy Path
# ---------------------------------------------------------------------------

def test_get_tracking_history_as_customer_returns_200(client, agent_token, customer_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    response = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 200


def test_get_tracking_history_as_agent_returns_200(client, agent_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    response = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 200


def test_get_tracking_history_as_admin_returns_200(client, agent_token, admin_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    response = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


def test_get_tracking_history_returns_list(client, agent_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    result = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()
    assert isinstance(result, list)
    assert len(result) == 1


def test_get_tracking_history_returns_all_updates_for_shipment(client, agent_token, sample_shipment_id):
    for i in range(3):
        client.post(
            f"/tracking/{sample_shipment_id}",
            headers={"Authorization": f"Bearer {agent_token}"},
            json={"location": f"Stop {i}", "status": "in_transit"},
        )
    result = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()
    assert len(result) == 3


def test_get_tracking_history_items_have_correct_fields(client, agent_token, sample_shipment_id):
    client.post(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub", "status": "in_transit"},
    )
    item = client.get(
        f"/tracking/{sample_shipment_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()[0]
    assert "id" in item
    assert "shipment_id" in item
    assert "location" in item
    assert "status" in item
    assert "updated_at" in item


def test_get_tracking_history_shipment_isolation(client, agent_token):
    """Updates for shipment A must not appear in shipment B's history."""
    shipment_a = str(uuid_lib.uuid4())
    shipment_b = str(uuid_lib.uuid4())

    # 2 updates for A, 1 for B
    client.post(
        f"/tracking/{shipment_a}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub A1", "status": "in_transit"},
    )
    client.post(
        f"/tracking/{shipment_a}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub A2", "status": "out_for_delivery"},
    )
    client.post(
        f"/tracking/{shipment_b}",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"location": "Hub B1", "status": "in_transit"},
    )

    result_a = client.get(
        f"/tracking/{shipment_a}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()
    result_b = client.get(
        f"/tracking/{shipment_b}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()

    assert len(result_a) == 2
    assert len(result_b) == 1


# ---------------------------------------------------------------------------
# Get Tracking History — Error Cases
# ---------------------------------------------------------------------------

def test_get_tracking_history_for_shipment_with_no_updates_returns_404(client, agent_token):
    no_updates_id = str(uuid_lib.uuid4())
    response = client.get(
        f"/tracking/{no_updates_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 404


def test_get_tracking_history_404_error_message(client, agent_token):
    no_updates_id = str(uuid_lib.uuid4())
    body = client.get(
        f"/tracking/{no_updates_id}",
        headers={"Authorization": f"Bearer {agent_token}"},
    ).json()
    assert "no tracking updates found" in body["detail"].lower()


def test_get_tracking_history_without_auth_returns_401(client, sample_shipment_id):
    response = client.get(f"/tracking/{sample_shipment_id}")
    assert response.status_code == 401
