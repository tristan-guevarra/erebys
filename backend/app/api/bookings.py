from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse
from app.api.deps import get_current_user, get_org_id, require_manager_or_above

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("", response_model=list[BookingResponse])
async def list_bookings(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    event_id: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Booking).where(Booking.organization_id == org_id)
    if event_id:
        query = query.where(Booking.event_id == event_id)
    if status:
        query = query.where(Booking.status == status)
    query = query.order_by(Booking.booked_at.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return [BookingResponse.model_validate(b) for b in result.scalars().all()]


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(
    body: BookingCreate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    # make sure the event exists and belongs to this org before booking
    event = await db.execute(
        select(Event).where(Event.id == body.event_id, Event.organization_id == org_id)
    )
    if not event.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Event not found")

    booking = Booking(
        event_id=body.event_id,
        athlete_id=body.athlete_id,
        organization_id=org_id,
        price_paid=body.price_paid,
        source=body.source,
        discount_applied=body.discount_applied,
        experiment_variant=body.experiment_variant,
    )
    db.add(booking)
    await db.flush()
    return BookingResponse.model_validate(booking)


@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    body: BookingUpdate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id, Booking.organization_id == org_id)
    )
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)
    await db.flush()
    return BookingResponse.model_validate(booking)
