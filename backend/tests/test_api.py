"""
integration tests — api endpoints with test database.
"""

import pytest
from httpx import AsyncClient

from app.models.organization import Organization
from app.models.user import User
from app.models.event import Event
from app.models.booking import Booking


# health
@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


# auth flow
@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient, seed_org: Organization):
    # register
    resp = await client.post("/api/v1/auth/register", json={
        "email": "new@test.com",
        "password": "securepass123",
        "full_name": "New User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    # login
    resp = await client.post("/api/v1/auth/login", json={
        "email": "new@test.com",
        "password": "securepass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, seed_admin):
    user, _ = seed_admin
    resp = await client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


# events crud
@pytest.mark.asyncio
async def test_list_events(
    client: AsyncClient, seed_org: Organization,
    seed_admin: tuple[User, str], seed_event: Event,
):
    _, token = seed_admin
    resp = await client.get(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": seed_org.id},
    )
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) >= 1
    assert events[0]["title"] == "Summer Striker Camp"


@pytest.mark.asyncio
async def test_create_event(
    client: AsyncClient, seed_org: Organization,
    seed_admin: tuple[User, str], seed_coach,
):
    _, token = seed_admin
    resp = await client.post(
        "/api/v1/events",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": seed_org.id},
        json={
            "title": "Winter Clinic",
            "event_type": "clinic",
            "capacity": 15,
            "base_price": 75.0,
            "current_price": 75.0,
            "start_date": "2026-03-15",
            "coach_id": seed_coach.id,
        },
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Winter Clinic"


# rbac: manager cannot create org
@pytest.mark.asyncio
async def test_manager_cannot_access_admin_route(
    client: AsyncClient, seed_org: Organization,
    seed_manager: tuple[User, str],
):
    _, token = seed_manager
    resp = await client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": seed_org.id},
    )
    assert resp.status_code == 403


# analytics
@pytest.mark.asyncio
async def test_analytics_overview(
    client: AsyncClient, seed_org: Organization,
    seed_admin: tuple[User, str], seed_booking: Booking,
):
    _, token = seed_admin
    resp = await client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": seed_org.id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "total_revenue" in data
    assert "total_bookings" in data


# pricing
@pytest.mark.asyncio
async def test_pricing_generate_recommendation(
    client: AsyncClient, seed_org: Organization,
    seed_admin: tuple[User, str], seed_event: Event,
):
    _, token = seed_admin
    resp = await client.post(
        f"/api/v1/pricing/recommendations/{seed_event.id}/generate",
        headers={"Authorization": f"Bearer {token}", "X-Organization-Id": seed_org.id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "suggested_price" in data
    assert "confidence_score" in data


# unauthenticated access
@pytest.mark.asyncio
async def test_unauthenticated_rejected(client: AsyncClient):
    resp = await client.get("/api/v1/events", headers={"X-Organization-Id": "fake"})
    assert resp.status_code in (401, 403)
