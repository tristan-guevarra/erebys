from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.analytics import (
    OverviewKPIs,
    RevenueByDay,
    CohortRow,
    AthleteLTVBucket,
    NoShowRisk,
)
from app.api.deps import get_org_id, require_manager_or_above
from app.services.analytics import (
    get_overview_kpis,
    get_revenue_by_day,
    get_cohort_retention,
    get_athlete_ltv_distribution,
    get_no_show_risks,
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview", response_model=OverviewKPIs)
async def overview(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    return await get_overview_kpis(db, org_id, days)


@router.get("/revenue", response_model=list[RevenueByDay])
async def revenue(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
):
    return await get_revenue_by_day(db, org_id, days)


@router.get("/cohorts", response_model=list[CohortRow])
async def cohorts(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    months: int = Query(6, ge=3, le=12),
    db: AsyncSession = Depends(get_db),
):
    return await get_cohort_retention(db, org_id, months)


@router.get("/ltv-distribution", response_model=list[AthleteLTVBucket])
async def ltv_distribution(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    db: AsyncSession = Depends(get_db),
):
    return await get_athlete_ltv_distribution(db, org_id)


@router.get("/no-show-risk", response_model=list[NoShowRisk])
async def no_show_risk(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_manager_or_above),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    return await get_no_show_risks(db, org_id, limit)
