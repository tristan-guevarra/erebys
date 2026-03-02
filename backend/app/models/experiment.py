import uuid
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, Integer, Text, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ExperimentStatus(str, enum.Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class Experiment(Base):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    event_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("events.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ExperimentStatus] = mapped_column(SAEnum(ExperimentStatus, values_callable=lambda x: [e.value for e in x]), default=ExperimentStatus.DRAFT)
    variant_a_price: Mapped[float] = mapped_column(Float, nullable=False)
    variant_b_price: Mapped[float] = mapped_column(Float, nullable=False)
    traffic_split: Mapped[float] = mapped_column(Float, default=0.5)  # % going to variant B
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    results: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assignments = relationship("ExperimentAssignment", back_populates="experiment", lazy="selectin")


class ExperimentAssignment(Base):
    __tablename__ = "experiment_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id: Mapped[str] = mapped_column(String(36), ForeignKey("experiments.id"), nullable=False)
    athlete_id: Mapped[str] = mapped_column(String(36), ForeignKey("athletes.id"), nullable=False)
    variant: Mapped[str] = mapped_column(String(1), nullable=False)  # "A" or "B"
    booking_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("bookings.id"), nullable=True)
    converted: Mapped[bool] = mapped_column(default=False)
    revenue: Mapped[float] = mapped_column(Float, default=0.0)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    experiment = relationship("Experiment", back_populates="assignments")
