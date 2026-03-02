from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


class AuditLogResponse(BaseModel):
    id: str
    action: str
    resource_type: str
    resource_id: str | None
    details: dict | None
    user_id: str | None
    created_at: str

    model_config = {"from_attributes": True}


class FeatureFlagResponse(BaseModel):
    id: str
    feature_key: str
    enabled: bool

    model_config = {"from_attributes": True}


class InsightReportResponse(BaseModel):
    id: str
    report_type: str
    period_start: str
    period_end: str
    narrative: str
    highlights: dict | None
    alerts: dict | None
    created_at: str

    model_config = {"from_attributes": True}
