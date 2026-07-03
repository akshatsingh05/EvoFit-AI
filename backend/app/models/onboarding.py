import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class OnboardingProfile(Base):
    """
    Stores the answers collected across the multi-step onboarding flow
    (Goals, Body Metrics, Fitness Experience, Lifestyle & Diet).
    Each step is stored as its own JSON blob so the frontend wizard
    can save partial progress step by step.
    """

    __tablename__ = "onboarding_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True, nullable=False)

    goals: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    body_metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    fitness_experience: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    lifestyle_diet: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="onboarding_profile")
