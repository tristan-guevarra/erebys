from pydantic import BaseModel
from datetime import datetime


class PricingRecommendationResponse(BaseModel):
    id: str
    event_id: str
    current_price: float
    suggested_price: float
    confidence_score: int
    price_change_pct: float
    expected_demand_change: float
    expected_revenue_change: float
    explanation: str | None
    drivers: dict | None
    model_version: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PriceChangeRequestCreate(BaseModel):
    event_id: str
    new_price: float
    reason: str | None = None
    recommendation_id: str | None = None


class PriceChangeRequestResponse(BaseModel):
    id: str
    event_id: str
    old_price: float
    new_price: float
    reason: str | None
    status: str
    requested_by: str
    reviewed_by: str | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}


class WhatIfRequest(BaseModel):
    event_id: str
    price_points: list[float]  # e.g., [80, 90, 100, 110, 120]


class ExperimentCreate(BaseModel):
    name: str
    description: str | None = None
    event_id: str | None = None
    variant_a_price: float
    variant_b_price: float
    traffic_split: float = 0.5


class ExperimentResponse(BaseModel):
    id: str
    organization_id: str
    event_id: str | None
    name: str
    description: str | None
    status: str
    variant_a_price: float
    variant_b_price: float
    traffic_split: float
    results: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}
