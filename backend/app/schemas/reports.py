from pydantic import BaseModel


class ReportSummary(BaseModel):
    period: str  # "weekly" | "monthly"
    start_date: str
    end_date: str
    workouts_completed: int
    workouts_skipped: int
    workout_frequency_pct: int  # % of scheduled training days completed
    total_calories_logged: int
    average_daily_protein_g: int
    weight_change_kg: float | None
    recovery_trend_available: bool
    ai_summary: str
