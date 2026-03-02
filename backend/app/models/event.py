import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class EventType(str, enum.Enum):
    CAMP = "camp"
    CLINIC = "clinic"
    PRIVATE = "private"


class EventStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    FULL = "full"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Event(Base):
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    coach_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("coaches.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[EventType] = mapped_column(SAEnum(EventType, values_callable=lambda x: [e.value for e in x]), nullable=False)
    status: Mapped[EventStatus] = mapped_column(SAEnum(EventStatus, values_callable=lambda x: [e.value for e in x]), default=EventStatus.PUBLISHED)
    capacity: Mapped[int] = mapped_column(Integer, default=20)
    booked_count: Mapped[int] = mapped_column(Integer, default=0)
    base_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_time: Mapped[str] = mapped_column(String(10), default="09:00")
    end_time: Mapped[str] = mapped_column(String(10), default="12:00")
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    skill_level: Mapped[str] = mapped_column(String(50), default="all")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="events")
    coach = relationship("Coach", back_populates="events")
    bookings = relationship("Booking", back_populates="event", lazy="selectin")
    ratings = relationship("Rating", back_populates="event", lazy="selectin")
    pricing_recommendations = relationship("PricingRecommendation", back_populates="event", lazy="selectin")

    @property
    def utilization_rate(self) -> float:
        if self.capacity == 0:
            return 0.0
        return round(self.booked_count / self.capacity * 100, 1)
