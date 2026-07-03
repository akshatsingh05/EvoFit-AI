from typing import Literal
from pydantic import BaseModel, Field


class GoalsStep(BaseModel):
    primary_goal: Literal["lose_weight", "build_muscle", "improve_endurance", "general_health", "sport_specific"]
    target_timeline_weeks: int = Field(ge=1, le=104)
    secondary_goals: list[str] = []


class BodyMetricsStep(BaseModel):
    height_cm: float = Field(gt=0, lt=300)
    weight_kg: float = Field(gt=0, lt=400)
    target_weight_kg: float | None = Field(default=None, gt=0, lt=400)
    age: int = Field(ge=13, le=100)
    sex: Literal["male", "female", "other"]


class FitnessExperienceStep(BaseModel):
    experience_level: Literal["beginner", "intermediate", "advanced"]
    workouts_per_week_current: int = Field(ge=0, le=14)
    preferred_workout_types: list[str] = []
    equipment_access: Literal["none", "home_basic", "full_gym"]


class LifestyleDietStep(BaseModel):
    diet_type: Literal["omnivore", "vegetarian", "vegan", "pescatarian", "keto", "other"]
    meals_per_day: int = Field(ge=1, le=8)
    sleep_hours_avg: float = Field(ge=0, le=24)
    stress_level: Literal["low", "moderate", "high"]
    occupation_activity: Literal["sedentary", "light", "active", "very_active"]


class OnboardingUpsertRequest(BaseModel):
    """All steps are optional so the wizard can PATCH progress one step at a time."""
    goals: GoalsStep | None = None
    body_metrics: BodyMetricsStep | None = None
    fitness_experience: FitnessExperienceStep | None = None
    lifestyle_diet: LifestyleDietStep | None = None


class OnboardingResponse(BaseModel):
    goals: dict | None = None
    body_metrics: dict | None = None
    fitness_experience: dict | None = None
    lifestyle_diet: dict | None = None
    is_complete: bool

    model_config = {"from_attributes": True}
