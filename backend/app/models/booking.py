import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    WAITLISTED = "waitlisted"
    PENDING = "pending"


class BookingSource(str, enum.Enum):
    PLATFORM = "platform"
    DIRECT = "direct"
    REFERRAL = "referral"
    IMPORT = "import"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id"), nullable=False)
    athlete_id: Mapped[str] = mapped_column(String(36), ForeignKey("athletes.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(SAEnum(BookingStatus, values_callable=lambda x: [e.value for e in x]), default=BookingStatus.CONFIRMED)
    source: Mapped[BookingSource] = mapped_column(SAEnum(BookingSource, values_callable=lambda x: [e.value for e in x]), default=BookingSource.PLATFORM)
    price_paid: Mapped[float] = mapped_column(Float, nullable=False)
    discount_applied: Mapped[float] = mapped_column(Float, default=0.0)
    experiment_variant: Mapped[str | None] = mapped_column(String(50), nullable=True)
    booked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="bookings")
    athlete = relationship("Athlete", back_populates="bookings")
    attendance = relationship("Attendance", back_populates="booking", uselist=False, lazy="selectin")
    payment = relationship("Payment", back_populates="booking", uselist=False, lazy="selectin")
