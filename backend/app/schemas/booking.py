from pydantic import BaseModel
from datetime import datetime


class BookingCreate(BaseModel):
    event_id: str
    athlete_id: str
    price_paid: float
    source: str = "platform"
    discount_applied: float = 0.0
    experiment_variant: str | None = None


class BookingUpdate(BaseModel):
    status: str | None = None
    price_paid: float | None = None


class BookingResponse(BaseModel):
    id: str
    event_id: str
    athlete_id: str
    organization_id: str
    status: str
    source: str
    price_paid: float
    discount_applied: float
    booked_at: datetime
    cancelled_at: datetime | None

    model_config = {"from_attributes": True}
