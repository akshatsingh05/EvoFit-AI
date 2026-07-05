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


class RecoveryHistoryEntry(BaseModel):
    created_at: str
    recovery_score: int


class RecommendationHistoryEntry(BaseModel):
    created_at: str
    recommendations: list[str]
    intensity_modifier: int


class CheckInHistoryEntry(BaseModel):
    checkin_date: date
    mood: str
    energy_level: int
    sleep_hours: float
    muscle_soreness: int
    pain_level: int


class ProgressResponse(BaseModel):
    weight_history: list[WeightLogEntry]
    workout_history: list[WorkoutHistoryEntry]
    nutrition_adherence: list[NutritionAdherenceEntry]
    workout_streak_days: int
    fitness_score: int
    recovery_trend: list[int] | None  # null until at least one adaptive insight exists
    total_calories_logged_today: int
    total_protein_logged_today: int

    recovery_history: list[RecoveryHistoryEntry]
    ai_recommendation_history: list[RecommendationHistoryEntry]
    checkin_history: list[CheckInHistoryEntry]
    workout_consistency_pct: int
    nutrition_consistency_pct: int
