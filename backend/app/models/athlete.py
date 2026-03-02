import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Athlete(Base):
    __tablename__ = "athletes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    skill_level: Mapped[str] = mapped_column(String(50), default="intermediate")  # beginner/intermediate/advanced
    ltv: Mapped[float] = mapped_column(Float, default=0.0)
    no_show_rate: Mapped[float] = mapped_column(Float, default=0.0)
    total_bookings: Mapped[int] = mapped_column(default=0)
    first_booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_booking_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="athletes")
    bookings = relationship("Booking", back_populates="athlete", lazy="selectin")
