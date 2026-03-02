from pydantic import BaseModel
from datetime import date


class OverviewKPIs(BaseModel):
    total_revenue: float
    revenue_change: float
    total_bookings: int
    bookings_change: float
    utilization_rate: float
    utilization_change: float
    no_show_rate: float
    no_show_change: float
    active_athletes: int
    athletes_change: float
    avg_ltv: float
    ltv_change: float
    cancellation_rate: float
    cancellation_change: float


class RevenueByDay(BaseModel):
    date: date
    revenue: float
    bookings: int


class CohortRow(BaseModel):
    cohort_month: str
    cohort_size: int
    retention: list[float]  # retention % for months 0, 1, 2, ...


class AthleteLTVBucket(BaseModel):
    bucket: str  # "$0-50", "$50-100", etc.
    count: int
    total_ltv: float
    avg_ltv: float


class NoShowRisk(BaseModel):
    athlete_id: str
    athlete_name: str
    risk_score: float  # 0-1
    risk_level: str  # low, medium, high
    total_bookings: int
    no_show_rate: float
    top_factors: list[str]


class MetricsTrend(BaseModel):
    dates: list[date]
    values: list[float]
    metric_name: str


class WhatIfResult(BaseModel):
    price: float
    estimated_demand: float
    estimated_revenue: float
    estimated_utilization: float
