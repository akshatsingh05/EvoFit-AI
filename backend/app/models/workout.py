import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, DateTime, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class WorkoutPlan(Base):
    """
    One generated weekly workout plan per user. `schedule` is a JSON list of
    7 day objects (see workout_ai_service for the shape). Regenerating creates
    a new row rather than mutating history, so past weeks remain inspectable.
    """

    __tablename__ = "workout_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    schedule: Mapped[list] = mapped_column(JSON, nullable=False)
    generation_basis: Mapped[dict] = mapped_column(JSON, nullable=False)  # snapshot of inputs used to generate it
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")


class WorkoutCompletion(Base):
    """Tracks completed/skipped status for a single day of a workout plan."""

    __tablename__ = "workout_completions"
    __table_args__ = (UniqueConstraint("user_id", "workout_date", name="uq_workout_completion_user_date"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("workout_plans.id"), nullable=False)
    workout_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # "completed" | "skipped"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
