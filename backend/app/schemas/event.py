from pydantic import BaseModel
from datetime import date, datetime


class EventCreate(BaseModel):
    title: str
    description: str | None = None
    event_type: str  # camp, clinic, private
    capacity: int = 20
    base_price: float
    current_price: float | None = None
    start_date: date
    end_date: date | None = None
    start_time: str = "09:00"
    end_time: str = "12:00"
    coach_id: str | None = None
    location: str | None = None
    skill_level: str = "all"


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    capacity: int | None = None
    current_price: float | None = None
    status: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    start_time: str | None = None
    end_time: str | None = None
    location: str | None = None
    skill_level: str | None = None


class EventResponse(BaseModel):
    id: str
    organization_id: str
    coach_id: str | None
    title: str
    description: str | None
    event_type: str
    status: str
    capacity: int
    booked_count: int
    base_price: float
    current_price: float
    start_date: date
    end_date: date | None
    start_time: str
    end_time: str
    location: str | None
    skill_level: str
    utilization_rate: float = 0.0
    created_at: datetime

    model_config = {"from_attributes": True}


class EventPerformance(BaseModel):
    event_id: str
    title: str
    event_type: str
    revenue: float
    bookings: int
    capacity: int
    utilization_rate: float
    no_show_rate: float
    avg_rating: float
    cancellation_rate: float
