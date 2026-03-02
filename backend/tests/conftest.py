"""
test configuration — fixtures for db, client, and auth helpers.
"""

import os
import uuid
import asyncio
from datetime import date, datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# override settings before importing app
os.environ["DATABASE_URL"] = "postgresql+asyncpg://erebys:erebys_secret@localhost:5432/erebys_test"
os.environ["DATABASE_URL_SYNC"] = "postgresql://erebys:erebys_secret@localhost:5432/erebys_test"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["JWT_SECRET"] = "test-secret-key"
os.environ["ENVIRONMENT"] = "test"

from app.main import app
from app.database import Base, get_db
from app.models.organization import Organization
from app.models.user import User, OrgUserRole, RoleEnum
from app.models.coach import Coach
from app.models.athlete import Athlete
from app.models.event import Event, EventType, EventStatus
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.attendance import Attendance
from app.services.auth import hash_password, create_access_token


TEST_DB_URL = os.environ["DATABASE_URL"]
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


def _uid() -> str:
    return str(uuid.uuid4())


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """create tables, yield session, then drop tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSession() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    """http test client with db override."""

    async def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


# seed helpers
@pytest_asyncio.fixture
async def seed_org(db_session: AsyncSession) -> Organization:
    org = Organization(
        id=_uid(), name="Test Academy", slug="test-academy",
        sport_type="soccer", region="US-East", competition_proxy=5.0,
    )
    db_session.add(org)
    await db_session.flush()
    return org


@pytest_asyncio.fixture
async def seed_admin(db_session: AsyncSession, seed_org: Organization) -> tuple[User, str]:
    user = User(
        id=_uid(), email="admin@test.com", hashed_password=hash_password("password123"),
        full_name="Test Admin", is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    role = OrgUserRole(id=_uid(), user_id=user.id, organization_id=seed_org.id, role=RoleEnum.ADMIN)
    db_session.add(role)
    await db_session.flush()

    token = create_access_token(user.id)
    return user, token


@pytest_asyncio.fixture
async def seed_manager(db_session: AsyncSession, seed_org: Organization) -> tuple[User, str]:
    user = User(
        id=_uid(), email="manager@test.com", hashed_password=hash_password("password123"),
        full_name="Test Manager", is_active=True,
    )
    db_session.add(user)
    await db_session.flush()

    role = OrgUserRole(id=_uid(), user_id=user.id, organization_id=seed_org.id, role=RoleEnum.MANAGER)
    db_session.add(role)
    await db_session.flush()

    token = create_access_token(user.id)
    return user, token


@pytest_asyncio.fixture
async def seed_coach(db_session: AsyncSession, seed_org: Organization) -> Coach:
    coach = Coach(
        id=_uid(), organization_id=seed_org.id, full_name="Coach Rivera",
        specialty="forward", hourly_rate=75.0, avg_rating=4.5,
    )
    db_session.add(coach)
    await db_session.flush()
    return coach


@pytest_asyncio.fixture
async def seed_athlete(db_session: AsyncSession, seed_org: Organization) -> Athlete:
    athlete = Athlete(
        id=_uid(), organization_id=seed_org.id, full_name="Liam Smith",
        email="liam@test.com", skill_level="intermediate",
        first_booking_date=date.today() - __import__("datetime").timedelta(days=60),
    )
    db_session.add(athlete)
    await db_session.flush()
    return athlete


@pytest_asyncio.fixture
async def seed_event(db_session: AsyncSession, seed_org: Organization, seed_coach: Coach) -> Event:
    event = Event(
        id=_uid(), organization_id=seed_org.id, coach_id=seed_coach.id,
        title="Summer Striker Camp", event_type=EventType.CAMP,
        status=EventStatus.PUBLISHED, capacity=20, booked_count=12,
        base_price=150.0, current_price=150.0,
        start_date=date.today() + __import__("datetime").timedelta(days=14),
        start_time="09:00", end_time="12:00", skill_level="intermediate",
    )
    db_session.add(event)
    await db_session.flush()
    return event


@pytest_asyncio.fixture
async def seed_booking(
    db_session: AsyncSession, seed_org: Organization,
    seed_event: Event, seed_athlete: Athlete,
) -> Booking:
    booking = Booking(
        id=_uid(), event_id=seed_event.id, athlete_id=seed_athlete.id,
        organization_id=seed_org.id, status=BookingStatus.CONFIRMED,
        price_paid=150.0, booked_at=datetime.utcnow(),
    )
    db_session.add(booking)
    await db_session.flush()

    # payment
    db_session.add(Payment(
        id=_uid(), booking_id=booking.id, organization_id=seed_org.id,
        amount=150.0, status=PaymentStatus.COMPLETED,
    ))
    await db_session.flush()
    return booking
