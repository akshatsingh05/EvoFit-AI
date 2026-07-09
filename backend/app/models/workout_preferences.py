import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class WorkoutPreferences(Base):
    """
    Sprint 4: Workout Preferences, editable any time from the Workout
    Preferences section. One row per user (same pattern as
    OnboardingProfile / UserSettings). Every generated workout plan is built
    from these values (see workout_service._build_context and
    services/ai/workout_generator.py) in addition to onboarding/medical data.

    `exercise_replacement_memory` is Sprint 4 objective 5 (User Preference
    Memory): a dict of {original_exercise_name: {replacement_name: count}},
    incremented every time the user replaces one exercise with another.
    Once a replacement has been chosen at least twice and is the dominant
    replacement for that exercise, future plans substitute it automatically.
    """

    __tablename__ = "workout_preferences"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True, nullable=False)

    workout_style: Mapped[str | None] = mapped_column(String, nullable=True)
    workout_location: Mapped[str | None] = mapped_column(String, nullable=True)  # gym | home | mixed
    equipment_available: Mapped[list] = mapped_column(JSON, default=list)
    preferred_duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    workout_intensity: Mapped[str | None] = mapped_column(String, nullable=True)  # light | moderate | high
    preferred_workout_time: Mapped[str | None] = mapped_column(String, nullable=True)  # morning | afternoon | evening
    favorite_muscle_groups: Mapped[list] = mapped_column(JSON, default=list)
    liked_exercises: Mapped[list] = mapped_column(JSON, default=list)
    disliked_exercises: Mapped[list] = mapped_column(JSON, default=list)
    avoid_movements: Mapped[list] = mapped_column(JSON, default=list)  # free-text, e.g. "No overhead press"

    exercise_replacement_memory: Mapped[dict] = mapped_column(JSON, default=dict)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User")
