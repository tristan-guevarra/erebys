from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class CategoryScore(BaseModel):
    category_name: str
    score: float
    notes: Optional[str] = None


class EvaluationCreate(BaseModel):
    athlete_id: str
    coach_id: str
    event_id: Optional[str] = None
    template_id: Optional[str] = None
    evaluation_type: str = "session"
    period_start: date
    period_end: date
    coach_notes: Optional[str] = None
    category_scores: list[CategoryScore] = []


class EvaluationUpdate(BaseModel):
    coach_notes: Optional[str] = None
    category_scores: Optional[list[CategoryScore]] = None
    overall_score: Optional[float] = None


class CategoryResponse(BaseModel):
    id: str
    category_name: str
    score: float
    previous_score: Optional[float]
    trend: str
    notes: Optional[str]
    display_order: int
    weight: float

    model_config = {"from_attributes": True}


class NarrativeResponse(BaseModel):
    id: str
    summary: str
    strengths: list[str]
    areas_for_improvement: list[str]
    recommendations: list[str]
    parent_friendly_summary: str

    model_config = {"from_attributes": True}


class EvaluationResponse(BaseModel):
    id: str
    organization_id: str
    athlete_id: str
    coach_id: Optional[str]
    event_id: Optional[str]
    template_id: Optional[str]
    evaluation_type: str
    period_start: date
    period_end: date
    overall_score: float
    status: str
    ai_generated: bool
    coach_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    categories: list[CategoryResponse] = []
    narrative: Optional[NarrativeResponse] = None
    # enriched fields (joined)
    athlete_name: Optional[str] = None
    coach_name: Optional[str] = None

    model_config = {"from_attributes": True}


class EvaluationListItem(BaseModel):
    id: str
    athlete_id: str
    athlete_name: str
    coach_id: Optional[str]
    coach_name: Optional[str]
    evaluation_type: str
    period_start: date
    period_end: date
    overall_score: float
    status: str
    ai_generated: bool
    created_at: datetime
    category_count: int


class EvaluationTemplateResponse(BaseModel):
    id: str
    organization_id: Optional[str]
    sport_type: str
    name: str
    categories: list[dict]
    is_default: bool

    model_config = {"from_attributes": True}


class EvalStatsResponse(BaseModel):
    total: int
    drafts: int
    published: int
    ai_generated: int
    this_month: int
    athletes_evaluated: int
