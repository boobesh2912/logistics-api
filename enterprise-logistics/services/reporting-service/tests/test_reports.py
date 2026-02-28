# tests/test_reports.py — reporting-service
"""
Comprehensive tests for the Reporting Service.
Covers: daily shipment reports, user listing, user deletion, role enforcement.
Data is seeded directly into the test DB sessions (no HTTP dependency on other services).
"""
import uuid as uuid_lib
from datetime import datetime, date, timedelta

from app.models.shipment import Shipment
from app.models.user import User


# ---------------------------------------------------------------------------
# Helpers — direct DB seeding
# ---------------------------------------------------------------------------

def seed_shipment(
    session,
    status="created",
    created_at=None,
    customer_id=None,
):
    if created_at is None:
        created_at = datetime.utcnow()
    shipment = Shipment(
        id=uuid_lib.uuid4(),
        tracking_number="TRK" + uuid_lib.uuid4().hex[:8].upper(),
        customer_id=customer_id or uuid_lib.uuid4(),
        source_address="Chennai",
        destination_address="Bangalore",
        status=status,
        created_at=created_at,
    )
    session.add(shipment)
    session.commit()
    return shipment


def seed_user(session, email=None, role="customer"):
    user = User(
        id=uuid_lib.uuid4(),
        email=email or f"user_{uuid_lib.uuid4().hex[:6]}@test.com",
        password_hash="hashed",
        role=role,
    )
    session.add(user)
    session.commit()
    return user


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

def test_health_check_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_body(client):
    body = client.get("/health").json()
    assert body["service"] == "reporting-service"
    assert body["status"] == "healthy"


# ---------------------------------------------------------------------------
# GET /reports — Happy Path
# ---------------------------------------------------------------------------

def test_get_reports_returns_200_as_admin(client, admin_token):
    response = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_get_reports_returns_zero_counts_when_db_is_empty(client, admin_token):
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["total_shipments_today"] == 0
    assert body["delivered"] == 0
    assert body["in_transit"] == 0


def test_get_reports_counts_shipments_created_today(client, admin_token, shipment_session):
    seed_shipment(shipment_session, status="created", created_at=datetime.utcnow())
    seed_shipment(shipment_session, status="created", created_at=datetime.utcnow())
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["total_shipments_today"] == 2


def test_get_reports_excludes_shipments_from_yesterday(client, admin_token, shipment_session):
    yesterday = datetime.utcnow() - timedelta(days=1)
    seed_shipment(shipment_session, status="created", created_at=datetime.utcnow())
    seed_shipment(shipment_session, status="created", created_at=yesterday)
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["total_shipments_today"] == 1


def test_get_reports_counts_delivered_shipments(client, admin_token, shipment_session):
    seed_shipment(shipment_session, status="delivered")
    seed_shipment(shipment_session, status="delivered")
    seed_shipment(shipment_session, status="in_transit")
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["delivered"] == 2


def test_get_reports_counts_in_transit_shipments(client, admin_token, shipment_session):
    seed_shipment(shipment_session, status="in_transit")
    seed_shipment(shipment_session, status="in_transit")
    seed_shipment(shipment_session, status="delivered")
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["in_transit"] == 2


def test_get_reports_response_schema(client, admin_token):
    """Response must have exactly the three required fields."""
    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert "total_shipments_today" in body
    assert "delivered" in body
    assert "in_transit" in body


def test_get_reports_all_counts_together(client, admin_token, shipment_session):
    """Combined scenario: 3 today, 1 delivered (today), 2 in_transit (today), 1 yesterday."""
    seed_shipment(shipment_session, status="delivered", created_at=datetime.utcnow())
    seed_shipment(shipment_session, status="in_transit", created_at=datetime.utcnow())
    seed_shipment(shipment_session, status="in_transit", created_at=datetime.utcnow())
    seed_shipment(shipment_session, status="created", created_at=datetime.utcnow() - timedelta(days=1))

    body = client.get("/reports", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert body["total_shipments_today"] == 3
    assert body["delivered"] == 1
    assert body["in_transit"] == 2


# ---------------------------------------------------------------------------
# GET /reports — Role Enforcement
# ---------------------------------------------------------------------------

def test_get_reports_as_customer_returns_403(client, customer_token):
    response = client.get("/reports", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 403


def test_get_reports_without_auth_returns_401(client):
    response = client.get("/reports")
    assert response.status_code == 401


def test_get_reports_with_invalid_token_returns_401(client):
    response = client.get("/reports", headers={"Authorization": "Bearer bad.token"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /admin/users — Happy Path
# ---------------------------------------------------------------------------

def test_get_all_users_returns_200_as_admin(client, admin_token, auth_session):
    seed_user(auth_session)
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200


def test_get_all_users_returns_list(client, admin_token, auth_session):
    seed_user(auth_session, email="user1@test.com")
    seed_user(auth_session, email="user2@test.com")
    result = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert isinstance(result, list)
    assert len(result) == 2


def test_get_all_users_response_items_contain_id_email_role(client, admin_token, auth_session):
    seed_user(auth_session, email="check@test.com", role="agent")
    items = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    item = items[0]
    assert "id" in item
    assert "email" in item
    assert "role" in item


def test_get_all_users_does_not_expose_password_hash(client, admin_token, auth_session):
    seed_user(auth_session)
    items = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert "password_hash" not in items[0]
    assert "password" not in items[0]


def test_get_all_users_returns_empty_list_when_no_users(client, admin_token):
    result = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    assert result == []


# ---------------------------------------------------------------------------
# GET /admin/users — Role Enforcement
# ---------------------------------------------------------------------------

def test_get_all_users_as_customer_returns_403(client, customer_token):
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == 403


def test_get_all_users_without_auth_returns_401(client):
    response = client.get("/admin/users")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# DELETE /admin/users/{id}
# ---------------------------------------------------------------------------

def test_delete_user_as_admin_returns_200(client, admin_token, auth_session):
    user = seed_user(auth_session)
    response = client.delete(
        f"/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200


def test_delete_user_returns_success_message(client, admin_token, auth_session):
    user = seed_user(auth_session)
    body = client.delete(
        f"/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    assert "deleted" in body["message"].lower()


def test_deleted_user_no_longer_appears_in_user_list(client, admin_token, auth_session):
    user = seed_user(auth_session, email="todelete@test.com")
    client.delete(
        f"/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    users = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"}).json()
    user_ids = [u["id"] for u in users]
    assert str(user.id) not in user_ids


def test_delete_nonexistent_user_returns_404(client, admin_token):
    fake_id = str(uuid_lib.uuid4())
    response = client.delete(
        f"/admin/users/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 404


def test_delete_nonexistent_user_error_message(client, admin_token):
    fake_id = str(uuid_lib.uuid4())
    body = client.delete(
        f"/admin/users/{fake_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    ).json()
    assert "not found" in body["detail"].lower()


def test_delete_user_as_customer_returns_403(client, customer_token, admin_token, auth_session):
    user = seed_user(auth_session)
    response = client.delete(
        f"/admin/users/{user.id}",
        headers={"Authorization": f"Bearer {customer_token}"},
    )
    assert response.status_code == 403


def test_delete_user_without_auth_returns_401(client, auth_session):
    user = seed_user(auth_session)
    response = client.delete(f"/admin/users/{user.id}")
    assert response.status_code == 401
