from datetime import date
from pydantic import BaseModel, Field


class WeightLogRequest(BaseModel):
    log_date: date
    weight_kg: float = Field(gt=0, lt=400)


class WeightLogEntry(BaseModel):
    log_date: date
    weight_kg: float

    model_config = {"from_attributes": True}


class WorkoutHistoryEntry(BaseModel):
    workout_date: date
    status: str


class NutritionAdherenceEntry(BaseModel):
    meal_date: date
    completed_count: int
    skipped_count: int
    total_count: int


class ProgressResponse(BaseModel):
    weight_history: list[WeightLogEntry]
    workout_history: list[WorkoutHistoryEntry]
    nutrition_adherence: list[NutritionAdherenceEntry]
    workout_streak_days: int
    fitness_score: int
    recovery_trend: list[int] | None  # null until Module 4 check-ins exist
    total_calories_logged_today: int
    total_protein_logged_today: int
