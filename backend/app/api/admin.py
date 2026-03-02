from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.models.feature_flag import FeatureFlag
from app.models.insight import InsightReport
from app.schemas.common import AuditLogResponse, FeatureFlagResponse, InsightReportResponse
from app.api.deps import get_org_id, require_admin, require_superadmin
from app.services.insights import generate_weekly_insight

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuditLog)
        .where(AuditLog.organization_id == org_id)
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return [AuditLogResponse.model_validate(log) for log in result.scalars().all()]


@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.organization_id == org_id)
    )
    return [FeatureFlagResponse.model_validate(f) for f in result.scalars().all()]


@router.patch("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def toggle_feature_flag(
    flag_id: str,
    enabled: bool,
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FeatureFlag).where(FeatureFlag.id == flag_id, FeatureFlag.organization_id == org_id)
    )
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    flag.enabled = enabled
    await db.flush()

    # log the toggle so there's a record of who flipped it
    db.add(AuditLog(
        organization_id=org_id,
        user_id=user.id,
        action="feature_flag_toggle",
        resource_type="feature_flag",
        resource_id=flag_id,
        details={"feature": flag.feature_key, "enabled": enabled},
    ))
    await db.flush()

    return FeatureFlagResponse.model_validate(flag)


@router.get("/insights", response_model=list[InsightReportResponse])
async def list_insights(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InsightReport)
        .where(InsightReport.organization_id == org_id)
        .order_by(InsightReport.created_at.desc())
        .limit(10)
    )
    return [InsightReportResponse.model_validate(r) for r in result.scalars().all()]


@router.post("/insights/generate", response_model=InsightReportResponse)
async def generate_insight(
    org_id: str = Depends(get_org_id),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    report = await generate_weekly_insight(db, org_id)
    return InsightReportResponse.model_validate(report)
