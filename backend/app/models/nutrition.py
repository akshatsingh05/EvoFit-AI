import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, DateTime, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class NutritionPlan(Base):
    """One generated daily nutrition target + meal plan per user per day."""

    __tablename__ = "nutrition_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    target_calories: Mapped[int] = mapped_column(nullable=False)
    target_protein_g: Mapped[int] = mapped_column(nullable=False)
    target_carbs_g: Mapped[int] = mapped_column(nullable=False)
    target_fat_g: Mapped[int] = mapped_column(nullable=False)
    water_goal_ml: Mapped[int] = mapped_column(nullable=False)
    meals: Mapped[list] = mapped_column(JSON, nullable=False)  # [{meal_type, name, calories, protein_g, ...}]
    generation_basis: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")


class MealCompletion(Base):
    """Tracks completed/skipped status for a single meal on a single date."""

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
