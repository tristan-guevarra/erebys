import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("events.id"), nullable=True)
    coach_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("coaches.id"), nullable=True)
    athlete_id: Mapped[str] = mapped_column(String(36), ForeignKey("athletes.id"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)  # 1.0 - 5.0
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="ratings")
    coach = relationship("Coach", back_populates="ratings")
