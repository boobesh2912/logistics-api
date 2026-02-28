# tests/test_shipments.py — shipment-service
"""
Comprehensive tests for the Shipment Service.
Covers: creation, listing, tracking, status updates, agent assignment, cancellation.
"""
import uuid as uuid_lib
from datetime import datetime, timedelta

from jose import jwt
from conftest import make_token

SECRET_KEY = "supersecretkey_logistics_2026"
ALGORITHM = "HS256"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def create_shipment(client, token, source="Chennai", destination="Bangalore"):
    return client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"source_address": source, "destination_address": destination},
    )


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    body = client.get("/health").json()
    assert body["service"] == "shipment-service"
    assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# Create Shipment — Happy Path
# ---------------------------------------------------------------------------

def test_create_shipment_as_customer_returns_201(client, customer_token):
    response = create_shipment(client, customer_token)
    assert response.status_code == 201


def test_create_shipment_response_has_tracking_number(client, customer_token):
    body = create_shipment(client, customer_token).json()
    assert "tracking_number" in body
    assert body["tracking_number"].startswith("TRK")


def test_create_shipment_tracking_number_length(client, customer_token):
    """TRK + 8 hex chars = 11 characters total."""
    tracking = create_shipment(client, customer_token).json()["tracking_number"]
    assert len(tracking) == 11


def test_create_shipment_initial_status_is_created(client, customer_token):
    body = create_shipment(client, customer_token).json()
    assert body["status"] == "created"


def test_create_shipment_response_contains_addresses(client, customer_token):
    body = create_shipment(client, customer_token, "Mumbai", "Delhi").json()
    assert body["source_address"] == "Mumbai"
    assert body["destination_address"] == "Delhi"


def test_create_shipment_response_contains_customer_id(client, customer_token):
    body = create_shipment(client, customer_token).json()
    assert "customer_id" in body
    assert body["customer_id"] is not None


def test_create_shipment_response_contains_id_and_created_at(client, customer_token):
    body = create_shipment(client, customer_token).json()
    assert "id" in body
    assert "created_at" in body


# ---------------------------------------------------------------------------
# Create Shipment — Role Enforcement
# ---------------------------------------------------------------------------

def test_create_shipment_as_agent_returns_403(client, agent_token):
    response = create_shipment(client, agent_token)
    assert response.status_code == 403


def test_create_shipment_as_admin_returns_403(client, admin_token):
    response = create_shipment(client, admin_token)
    assert response.status_code == 403


def test_create_shipment_without_auth_returns_401(client):
    response = client.post("/shipments/", json={
        "source_address": "Chennai", "destination_address": "Bangalore"
    })
    assert response.status_code == 401


def test_create_shipment_with_invalid_token_returns_401(client):
    response = client.post(
        "/shipments/",
        headers={"Authorization": "Bearer invalidtoken"},
        json={"source_address": "A", "destination_address": "B"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create Shipment — Validation
# ---------------------------------------------------------------------------

def test_create_shipment_missing_source_address_returns_422(client, customer_token):
    response = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"destination_address": "Bangalore"},
    )
    assert response.status_code == 422


def test_create_shipment_missing_destination_address_returns_422(client, customer_token):
    response = client.post(
        "/shipments/",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"source_address": "Chennai"},
    )
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# List Shipments
# ---------------------------------------------------------------------------

def test_list_shipments_returns_empty_list_for_new_customer(client, customer_token):
    response = client.get("/shipments/", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_shipments_returns_all_shipments_for_customer(client, customer_token):
    create_shipment(client, customer_token)
    create_shipment(client, customer_token, "Pune", "Hyderabad")
    response = client.get("/shipments/", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_shipments_customer_isolation(client, customer_uid, agent_uid):
    """Customer A should only see their own shipments, not Customer B's."""
    token_a = make_token("customer", uid=customer_uid)
    token_b = make_token("customer", uid=agent_uid)

    create_shipment(client, token_a)
    create_shipment(client, token_a)
    create_shipment(client, token_b)  # Different customer

    response = client.get("/shipments/", headers={"Authorization": f"Bearer {token_a}"})
    assert len(response.json()) == 2


def test_list_shipments_without_auth_returns_401(client):
    response = client.get("/shipments/")
    assert response.status_code == 401


def test_list_shipments_as_agent_returns_403(client, agent_token):
    response = client.get("/shipments/", headers={"Authorization": f"Bearer {agent_token}"})
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Track Shipment by Tracking Number
# ---------------------------------------------------------------------------

def test_track_shipment_returns_200(client, customer_token):
    shipment = create_shipment(client, customer_token).json()
    tracking_number = shipment["tracking_number"]
    response = client.get(
        f"/shipments/{tracking_number}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 200


def test_track_shipment_response_contains_tracking_number_and_status(client, customer_token):
    shipment = create_shipment(client, customer_token).json()
    tracking_number = shipment["tracking_number"]
    body = client.get(
        f"/shipments/{tracking_number}",
        headers={"Authorization": f"Bearer {customer_token}"},
    ).json()
    assert body["tracking_number"] == tracking_number
    assert body["status"] == "created"


def test_track_nonexistent_shipment_returns_404(client, customer_token):
    response = client.get(
        "/shipments/TRKNONEXIST",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 404


def test_track_shipment_without_auth_returns_401(client):
    response = client.get("/shipments/TRK12345678")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Assign Agent
# ---------------------------------------------------------------------------

def test_assign_agent_as_admin_returns_200(client, customer_token, admin_token, agent_uid):
    shipment = create_shipment(client, customer_token).json()
    response = client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    assert response.status_code == 200


def test_assign_agent_response_contains_agent_id(client, customer_token, admin_token, agent_uid):
    shipment = create_shipment(client, customer_token).json()
    body = client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    ).json()
    assert body["agent_id"] == agent_uid


def test_assign_agent_as_customer_returns_403(client, customer_token, agent_uid):
    shipment = create_shipment(client, customer_token).json()
    response = client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"agent_id": agent_uid},
    )
    assert response.status_code == 403


def test_assign_agent_as_agent_returns_403(client, customer_token, agent_token, agent_uid):
    shipment = create_shipment(client, customer_token).json()
    response = client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"agent_id": agent_uid},
    )
    assert response.status_code == 403


def test_assign_agent_to_nonexistent_shipment_returns_404(client, admin_token, agent_uid):
    fake_id = str(uuid_lib.uuid4())
    response = client.put(
        f"/shipments/{fake_id}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Update Status
# ---------------------------------------------------------------------------

def test_assigned_agent_can_update_status_to_in_transit(client, customer_token, admin_token, agent_uid):
    agent_token = make_token("agent", uid=agent_uid)
    shipment = create_shipment(client, customer_token).json()

    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem Hub"},
    )
    assert response.status_code == 200


def test_status_update_persists_new_status(client, customer_token, admin_token, agent_uid):
    agent_token = make_token("agent", uid=agent_uid)
    shipment = create_shipment(client, customer_token).json()

    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    body = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem Hub"},
    ).json()
    assert body["status"] == "in_transit"


def test_agent_can_update_status_to_out_for_delivery(client, customer_token, admin_token, agent_uid):
    agent_token = make_token("agent", uid=agent_uid)
    shipment = create_shipment(client, customer_token).json()
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "out_for_delivery", "location": "Bangalore Hub"},
    )
    assert response.status_code == 200


def test_agent_can_update_status_to_delivered(client, customer_token, admin_token, agent_uid):
    agent_token = make_token("agent", uid=agent_uid)
    shipment = create_shipment(client, customer_token).json()
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "delivered", "location": "Bangalore"},
    )
    assert response.status_code == 200


def test_unassigned_agent_cannot_update_status(client, customer_token, admin_token, agent_uid):
    """An agent who is NOT assigned to the shipment must get 403."""
    assigned_uid = str(uuid_lib.uuid4())
    unassigned_token = make_token("agent", uid=agent_uid)  # different uid from assigned

    shipment = create_shipment(client, customer_token).json()
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": assigned_uid},
    )
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {unassigned_token}"},
        json={"status": "in_transit", "location": "X"},
    )
    assert response.status_code == 403


def test_status_update_with_invalid_status_value_returns_400(client, customer_token, admin_token, agent_uid):
    agent_token = make_token("agent", uid=agent_uid)
    shipment = create_shipment(client, customer_token).json()
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "flying", "location": "X"},
    )
    assert response.status_code == 400


def test_customer_cannot_update_shipment_status(client, customer_token, admin_token, agent_uid):
    shipment = create_shipment(client, customer_token).json()
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {customer_token}"},
        json={"status": "in_transit", "location": "X"},
    )
    assert response.status_code == 403


def test_update_status_without_auth_returns_401(client, customer_token):
    shipment = create_shipment(client, customer_token).json()
    response = client.put(
        f"/shipments/{shipment['id']}/status",
        json={"status": "in_transit", "location": "X"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Cancel Shipment
# ---------------------------------------------------------------------------

def test_customer_can_cancel_own_created_shipment(client, customer_uid):
    token = make_token("customer", uid=customer_uid)
    shipment = create_shipment(client, token).json()
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_cancel_shipment_returns_success_message(client, customer_uid):
    token = make_token("customer", uid=customer_uid)
    shipment = create_shipment(client, token).json()
    body = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    assert "cancelled" in body["message"].lower()


def test_cancel_dispatched_shipment_returns_400(client, customer_uid, admin_token, agent_uid):
    """Cannot cancel a shipment that has been moved past 'created' status."""
    customer_token = make_token("customer", uid=customer_uid)
    agent_token = make_token("agent", uid=agent_uid)

    shipment = create_shipment(client, customer_token).json()
    client.put(
        f"/shipments/{shipment['id']}/assign-agent",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"agent_id": agent_uid},
    )
    client.put(
        f"/shipments/{shipment['id']}/status",
        headers={"Authorization": f"Bearer {agent_token}"},
        json={"status": "in_transit", "location": "Salem"},
    )
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 400


def test_cancel_another_customers_shipment_returns_403(client, customer_uid, agent_uid):
    """Customer B cannot cancel Customer A's shipment."""
    token_a = make_token("customer", uid=customer_uid)
    token_b = make_token("customer", uid=agent_uid)

    shipment = create_shipment(client, token_a).json()
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert response.status_code == 403


def test_cancel_nonexistent_shipment_returns_404(client, customer_token):
    fake_id = str(uuid_lib.uuid4())
    response = client.delete(
        f"/shipments/{fake_id}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 404


def test_cancel_shipment_without_auth_returns_401(client, customer_token):
    shipment = create_shipment(client, customer_token).json()
    response = client.delete(f"/shipments/{shipment['id']}")
    assert response.status_code == 401


def test_agent_cannot_cancel_shipment(client, customer_token, agent_token):
    shipment = create_shipment(client, customer_token).json()
    response = client.delete(
        f"/shipments/{shipment['id']}",
        headers={"Authorization": f"Bearer {agent_token}"},
    )
    assert response.status_code == 403
