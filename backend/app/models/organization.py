import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sport_type: Mapped[str] = mapped_column(String(100), default="multi")
    region: Mapped[str] = mapped_column(String(100), default="US-East")
    competition_proxy: Mapped[float] = mapped_column(Float, default=5.0)  # 1-10 scale
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    members = relationship("OrgUserRole", back_populates="organization", lazy="selectin")
    coaches = relationship("Coach", back_populates="organization", lazy="selectin")
    athletes = relationship("Athlete", back_populates="organization", lazy="selectin")
    events = relationship("Event", back_populates="organization", lazy="selectin")
    feature_flags = relationship("FeatureFlag", back_populates="organization", lazy="selectin")
