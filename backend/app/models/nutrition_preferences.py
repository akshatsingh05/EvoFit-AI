import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class NutritionPreferences(Base):
    """
    Sprint 4: Nutrition Preferences, editable any time from the Nutrition
    Preferences section. One row per user. Every generated nutrition plan is
    built from these values (see nutrition_service._build_base_context and
    services/ai/nutrition_generator.py) in addition to onboarding/medical data.

    `meal_replacement_memory` mirrors WorkoutPreferences.exercise_replacement_memory
    (Sprint 4 objective 5): {original_meal_name: {replacement_name: count}}.
    """

    __tablename__ = "nutrition_preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True, nullable=False)

    diet_type: Mapped[str | None] = mapped_column(String, nullable=True)  # vegetarian|vegan|eggetarian|non_vegetarian
    cuisine_preference: Mapped[str | None] = mapped_column(String, nullable=True)
    budget: Mapped[str | None] = mapped_column(String, nullable=True)  # low | medium | high
    meals_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    favorite_foods: Mapped[list] = mapped_column(JSON, default=list)
    disliked_foods: Mapped[list] = mapped_column(JSON, default=list)
    allergies: Mapped[list] = mapped_column(JSON, default=list)
    water_goal_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    preferred_snacks: Mapped[list] = mapped_column(JSON, default=list)
    cooking_time_preference: Mapped[str | None] = mapped_column(String, nullable=True)  # quick|moderate|anything

    meal_replacement_memory: Mapped[dict] = mapped_column(JSON, default=dict)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
