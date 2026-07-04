from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout import WorkoutCompletion
from app.models.nutrition import MealCompletion, NutritionPlan
from app.models.progress import WeightLog

PERIOD_DAYS = {"weekly": 7, "monthly": 30}


def _date_range(period: str) -> tuple[date, date]:
    days = PERIOD_DAYS.get(period, 7)
    end = date.today()
    start = end - timedelta(days=days - 1)
    return start, end


def _generate_ai_summary(
    period: str, workouts_completed: int, workouts_skipped: int, weight_change_kg: float | None
) -> str:
    """
    Rule-based summary from the period's real numbers. Placeholder for an
    LLM-generated summary (see app/services/ai/) once that integration exists.
    """
    total = workouts_completed + workouts_skipped
    if total == 0:
        return f"No workouts were logged this {period[:-2] if period.endswith('ly') else period} period yet."

    frequency_note = f"You completed {workouts_completed} of {total} logged workouts"
    weight_note = ""
    if weight_change_kg is not None:
        direction = "down" if weight_change_kg < 0 else "up" if weight_change_kg > 0 else "steady at"
        weight_note = f", and your weight moved {direction} {abs(weight_change_kg):.1f} kg"
    return f"{frequency_note}{weight_note} over this {period} period."


def get_report(db: Session, user: User, period: str) -> dict:
    start, end = _date_range(period)

    workout_rows = (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.user_id == user.id, WorkoutCompletion.workout_date.between(start, end))
        .all()
    )
    workouts_completed = sum(1 for r in workout_rows if r.status == "completed")
    workouts_skipped = sum(1 for r in workout_rows if r.status == "skipped")
    total_workouts_logged = workouts_completed + workouts_skipped
    workout_frequency_pct = round((workouts_completed / total_workouts_logged) * 100) if total_workouts_logged else 0

    meal_rows = (
        db.query(MealCompletion)
        .filter(
            MealCompletion.user_id == user.id,
            MealCompletion.meal_date.between(start, end),
            MealCompletion.status == "completed",
        )
        .all()
    )
    total_calories = 0
    total_protein = 0
    days_with_meals = set()
    plan_cache: dict[str, NutritionPlan] = {}
    for row in meal_rows:
        plan = plan_cache.get(row.plan_id)
        if plan is None:
            plan = db.query(NutritionPlan).filter(NutritionPlan.id == row.plan_id).first()
            plan_cache[row.plan_id] = plan
        if plan is None:
            continue
        meal = next((m for m in plan.meals if m["meal_type"] == row.meal_type), None)
        if meal:
            total_calories += meal["calories"]
            total_protein += meal["protein_g"]
            days_with_meals.add(row.meal_date)

    avg_daily_protein = round(total_protein / len(days_with_meals)) if days_with_meals else 0

    weight_rows = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id, WeightLog.log_date.between(start, end))
        .order_by(WeightLog.log_date.asc())
        .all()
    )
    weight_change_kg = round(weight_rows[-1].weight_kg - weight_rows[0].weight_kg, 1) if len(weight_rows) >= 2 else None

    ai_summary = _generate_ai_summary(period, workouts_completed, workouts_skipped, weight_change_kg)

    return {
        "period": period,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "workouts_completed": workouts_completed,
        "workouts_skipped": workouts_skipped,
        "workout_frequency_pct": workout_frequency_pct,
        "total_calories_logged": total_calories,
        "average_daily_protein_g": avg_daily_protein,
        "weight_change_kg": weight_change_kg,
        "recovery_trend_available": False,
        "ai_summary": ai_summary,
    }
