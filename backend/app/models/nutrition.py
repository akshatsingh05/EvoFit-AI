import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, DateTime, Date, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class NutritionPlan(Base):
    """
    One generated weekly nutrition plan per user, mirroring WorkoutPlan's
    architecture exactly (Sprint 2). `days` is a JSON list of 7 day objects:
    {day_name, date, target_calories, target_protein_g, target_carbs_g,
    target_fat_g, water_goal_ml, meals: [...]}. Regenerating creates a new
    row rather than mutating history, so past weeks remain inspectable.
    """

    __table_args__ = (Index("ix_nutrition_plans_user_week", "user_id", "week_start_date"),)

    __tablename__ = "nutrition_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    week_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    days: Mapped[list] = mapped_column(JSON, nullable=False)
    generation_basis: Mapped[dict] = mapped_column(JSON, nullable=False)  # snapshot of inputs used to generate it
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")


class MealCompletion(Base):
    """Tracks completed/skipped status for a single meal on a single date (unchanged from Sprint 1).
    `plan_id` now points at the weekly NutritionPlan that contains `meal_date`."""

    __tablename__ = "meal_completions"
    __table_args__ = (
        UniqueConstraint("user_id", "meal_date", "meal_type", name="uq_meal_completion_user_date_type"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    plan_id: Mapped[str] = mapped_column(String, ForeignKey("nutrition_plans.id"), nullable=False)
    meal_date: Mapped[date] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False)  # breakfast | lunch | snack | dinner
    status: Mapped[str] = mapped_column(String, nullable=False)  # "completed" | "skipped"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
