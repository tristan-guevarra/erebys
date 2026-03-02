import uuid
from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class MetricsDaily(Base):
    __tablename__ = "metrics_daily"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    # revenue and booking counts for the day
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0)
    booking_count: Mapped[int] = mapped_column(Integer, default=0)
    cancellation_count: Mapped[int] = mapped_column(Integer, default=0)

    # how full were the sessions
    total_capacity: Mapped[int] = mapped_column(Integer, default=0)
    total_booked: Mapped[int] = mapped_column(Integer, default=0)
    utilization_rate: Mapped[float] = mapped_column(Float, default=0.0)

    # attendance quality metrics
    no_show_count: Mapped[int] = mapped_column(Integer, default=0)
    no_show_rate: Mapped[float] = mapped_column(Float, default=0.0)
    late_cancel_count: Mapped[int] = mapped_column(Integer, default=0)

    # athlete engagement snapshot
    active_athletes: Mapped[int] = mapped_column(Integer, default=0)
    new_athletes: Mapped[int] = mapped_column(Integer, default=0)
    avg_ltv: Mapped[float] = mapped_column(Float, default=0.0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
