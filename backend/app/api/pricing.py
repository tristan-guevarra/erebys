from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.event import Event
from app.models.organization import Organization
from app.models.user import User
from app.models.pricing import PricingRecommendation, PriceChangeRequest, ChangeRequestStatus
from app.models.audit import AuditLog
from app.schemas.pricing import (
    PricingRecommendationResponse,
    PriceChangeRequestCreate,
    PriceChangeRequestResponse,
    WhatIfRequest,
)
from app.schemas.analytics import WhatIfResult
from app.api.deps import get_org_id, require_manager_or_above, require_admin
from app.services.ml_engine import generate_pricing_recommendation, what_if_simulation

router = APIRouter(prefix="/pricing", tags=["Pricing"])


@router.get("/recommendations", response_model=list[PricingRecommendationResponse])
async def list_recommendations(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    event_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(PricingRecommendation).where(PricingRecommendation.organization_id == org_id)
    if event_id:
        query = query.where(PricingRecommendation.event_id == event_id)
    query = query.order_by(PricingRecommendation.created_at.desc()).limit(50)

    result = await db.execute(query)
    return [PricingRecommendationResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/recommendations/{event_id}/generate", response_model=PricingRecommendationResponse)
async def generate_recommendation(
    event_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    """runs the ml engine on this event and saves a fresh pricing recommendation"""
    event = await db.execute(
        select(Event).where(Event.id == event_id, Event.organization_id == org_id)
    )
    event = event.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    org = await db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    result = await generate_pricing_recommendation(db, event, org)

    rec = PricingRecommendation(
        event_id=event.id,
        organization_id=org_id,
        current_price=event.current_price,
        suggested_price=result.suggested_price,
        confidence_score=result.confidence_score,
        price_change_pct=result.price_change_pct,
        expected_demand_change=result.expected_demand_change,
        expected_revenue_change=result.expected_revenue_change,
        explanation=result.explanation,
        drivers=result.drivers,
    )
    db.add(rec)
    await db.flush()
    return PricingRecommendationResponse.model_validate(rec)


@router.post("/what-if", response_model=list[WhatIfResult])
async def what_if(
    body: WhatIfRequest,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    """simulates demand and revenue at different price points for an event"""
    event = await db.execute(
        select(Event).where(Event.id == body.event_id, Event.organization_id == org_id)
    )
    event = event.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    org = await db.get(Organization, org_id)
    results = await what_if_simulation(db, event, org, body.price_points)
    return [WhatIfResult(**r) for r in results]


@router.post("/change-requests", response_model=PriceChangeRequestResponse, status_code=201)
async def create_change_request(
    body: PriceChangeRequestCreate,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    """submits a price change for admin approval — starts the approval workflow"""
    event = await db.execute(
        select(Event).where(Event.id == body.event_id, Event.organization_id == org_id)
    )
    event = event.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    req = PriceChangeRequest(
        event_id=event.id,
        organization_id=org_id,
        recommendation_id=body.recommendation_id,
        requested_by=user.id,
        old_price=event.current_price,
        new_price=body.new_price,
        reason=body.reason,
    )
    db.add(req)
    await db.flush()
    return PriceChangeRequestResponse.model_validate(req)


@router.get("/change-requests", response_model=list[PriceChangeRequestResponse])
async def list_change_requests(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(PriceChangeRequest).where(PriceChangeRequest.organization_id == org_id)
    if status:
        query = query.where(PriceChangeRequest.status == status)
    query = query.order_by(PriceChangeRequest.created_at.desc())

    result = await db.execute(query)
    return [PriceChangeRequestResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/change-requests/{request_id}/approve", response_model=PriceChangeRequestResponse)
async def approve_change_request(
    request_id: str,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """admin approves the request and the new price gets applied immediately"""
    result = await db.execute(
        select(PriceChangeRequest).where(
            PriceChangeRequest.id == request_id,
            PriceChangeRequest.organization_id == org_id,
        )
    )
    req = result.scalar_one_or_none()
    if not req:
        raise HTTPException(status_code=404, detail="Change request not found")

    if req.status != ChangeRequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already processed")

    # actually apply the new price to the event
    event = await db.get(Event, req.event_id)
    if event:
        event.current_price = req.new_price

    req.status = ChangeRequestStatus.APPLIED
    req.reviewed_by = user.id
    req.reviewed_at = datetime.utcnow()

    # write an audit log entry so we have a trail
    db.add(AuditLog(
        organization_id=org_id,
        user_id=user.id,
        action="price_change_approved",
        resource_type="event",
        resource_id=req.event_id,
        details={"old_price": req.old_price, "new_price": req.new_price},
    ))

    await db.flush()
    return PriceChangeRequestResponse.model_validate(req)
