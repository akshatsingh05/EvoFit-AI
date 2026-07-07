from datetime import datetime
from pydantic import BaseModel


class PlanInfoSchema(BaseModel):
    """
    Shared "why did I get this plan" summary, rendered at the top of both the
    Workout and Nutrition pages. Domain-specific fields (workout_days /
    calories_target) are optional so one schema covers both.
    """

    generated_on: datetime
    current_goal: str | None = None
    difficulty: str | None = None
    workout_days: int | None = None
    calories_target: int | None = None
    plan_version: int
    last_regenerated_at: datetime | None = None
