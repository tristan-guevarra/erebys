from pydantic import BaseModel
from typing import Optional


class PlatformOverview(BaseModel):
    total_revenue_30d: float
    active_academies: int
    total_athletes: int
    total_events_month: int
    platform_utilization: float
    mrr: float
    revenue_growth_pct: float
    total_pending_changes: int


class AcademyMetrics(BaseModel):
    id: str
    name: str
    sport_type: str
    region: str
    monthly_revenue: float
    active_athletes: int
    events_count: int
    utilization_rate: float
    health_score: int
    athlete_retention_rate: float
    created_at: str


class PlatformRevenueDay(BaseModel):
    date: str
    total: float
    by_org: dict  # org_name -> revenue


class PlatformUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    is_active: bool
    is_superadmin: bool
    created_at: str
    orgs: list[dict]  # [{org_id, org_name, role}]


class SystemHealth(BaseModel):
    db_status: str
    db_pool_size: int
    redis_status: str
    celery_status: str
    last_metrics_run: Optional[str]
    last_insight_run: Optional[str]
    api_version: str
    uptime_status: str
