from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.event import Event, EventType, EventStatus
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventResponse, EventPerformance
from app.api.deps import get_current_user, get_org_id, require_manager_or_above
from app.services.analytics import get_event_performance

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    event_type: str | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Event).where(Event.organization_id == org_id)
    if event_type:
        query = query.where(Event.event_type == event_type)
    if status:
        query = query.where(Event.status == status)
    query = query.order_by(Event.start_date.desc()).offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    events = result.scalars().all()
    return [EventResponse.model_validate(e) for e in events]


@router.get("/performance", response_model=list[EventPerformance])
async def event_performance(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    return await get_event_performance(db, org_id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.organization_id == org_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventResponse.model_validate(event)


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(
    body: EventCreate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    event = Event(
        organization_id=org_id,
        title=body.title,
        description=body.description,
        event_type=EventType(body.event_type),
        capacity=body.capacity,
        base_price=body.base_price,
        current_price=body.current_price or body.base_price,
        start_date=body.start_date,
        end_date=body.end_date,
        start_time=body.start_time,
        end_time=body.end_time,
        coach_id=body.coach_id,
        location=body.location,
        skill_level=body.skill_level,
    )
    db.add(event)
    await db.flush()
    return EventResponse.model_validate(event)


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    body: EventUpdate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.organization_id == org_id)
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    await db.flush()
    return EventResponse.model_validate(event)
