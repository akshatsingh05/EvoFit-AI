from pydantic import BaseModel


class WorkoutSummary(BaseModel):
    status: str  # "not_generated" | "scheduled" | "completed" | "rest_day"
    title: str | None = None
    exercise_count: int | None = None


class NutritionSummary(BaseModel):
    status: str  # "not_generated" | "on_track" | "logged"
    target_calories: int | None = None
    logged_calories: int | None = None


class WeeklyProgressPoint(BaseModel):
    day_label: str  # "Mon", "Tue", ...
    workouts_completed: int
    has_checkin: bool


class DashboardResponse(BaseModel):
    full_name: str
    has_completed_onboarding: bool

    today_workout: WorkoutSummary
    today_nutrition: NutritionSummary

    recovery_score: int | None  # null until daily check-ins exist (Module 4)
    workout_streak_days: int
    fitness_score: int  # baseline score derived from onboarding profile
    fitness_score_basis: str  # explains what the score is derived from

    weekly_progress: list[WeeklyProgressPoint]

    ai_coach_tip: str

    quick_actions_available: list[str]  # which quick actions are meaningful right now
