import uuid
import enum
from datetime import datetime, date
from sqlalchemy import String, DateTime, Date, Float, Integer, Boolean, Text, ForeignKey, JSON, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class EvaluationType(str, enum.Enum):
    SESSION = "session"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class EvaluationStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class EvaluationTemplate(Base):
    __tablename__ = "evaluation_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    sport_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    categories: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)  # [{name, weight}]
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    athlete_id: Mapped[str] = mapped_column(String(36), ForeignKey("athletes.id", ondelete="CASCADE"), nullable=False)
    coach_id: Mapped[str] = mapped_column(String(36), ForeignKey("coaches.id", ondelete="SET NULL"), nullable=True)
    event_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    template_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("evaluation_templates.id", ondelete="SET NULL"), nullable=True)
    evaluation_type: Mapped[EvaluationType] = mapped_column(
        SAEnum(EvaluationType, values_callable=lambda x: [e.value for e in x]),
        default=EvaluationType.SESSION,
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[EvaluationStatus] = mapped_column(
        SAEnum(EvaluationStatus, values_callable=lambda x: [e.value for e in x]),
        default=EvaluationStatus.DRAFT,
    )
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    coach_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship("EvaluationCategory", back_populates="evaluation", lazy="selectin", cascade="all, delete-orphan")
    narrative = relationship("EvaluationNarrative", back_populates="evaluation", uselist=False, lazy="selectin", cascade="all, delete-orphan")


class EvaluationCategory(Base):
    __tablename__ = "evaluation_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False)
    category_name: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=5.0)
    previous_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    trend: Mapped[str] = mapped_column(String(20), default="stable")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    weight: Mapped[float] = mapped_column(Float, default=1.0)

    evaluation = relationship("Evaluation", back_populates="categories")


class EvaluationNarrative(Base):
    __tablename__ = "evaluation_narratives"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluations.id", ondelete="CASCADE"), nullable=False, unique=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    strengths: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    areas_for_improvement: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    parent_friendly_summary: Mapped[str] = mapped_column(Text, nullable=False)

    evaluation = relationship("Evaluation", back_populates="narrative")
