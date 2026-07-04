from datetime import date
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.progress import WeightLog
from app.models.nutrition import MealCompletion, NutritionPlan
from app.services import workout_service, onboarding_service
from app.services.dashboard_service import _compute_fitness_score


def _seed_weight_log_if_needed(db: Session, user: User) -> None:
    has_any = db.query(WeightLog).filter(WeightLog.user_id == user.id).first()
    if has_any:
        return
    onboarding = onboarding_service.get_onboarding(db, user)
    body_metrics = onboarding.body_metrics
    if body_metrics and body_metrics.get("weight_kg"):
        seed = WeightLog(user_id=user.id, log_date=date.today(), weight_kg=body_metrics["weight_kg"])
        db.add(seed)
        db.commit()


def log_weight(db: Session, user: User, log_date: date, weight_kg: float) -> WeightLog:
    existing = db.query(WeightLog).filter(WeightLog.user_id == user.id, WeightLog.log_date == log_date).first()
    if existing:
        existing.weight_kg = weight_kg
        db.commit()
        db.refresh(existing)
        return existing
    entry = WeightLog(user_id=user.id, log_date=log_date, weight_kg=weight_kg)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def get_weight_history(db: Session, user: User, limit: int = 90) -> list[WeightLog]:
    _seed_weight_log_if_needed(db, user)
    return (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.log_date.asc())
        .limit(limit)
        .all()
    )


def get_nutrition_adherence(db: Session, user: User, limit_days: int = 14) -> list[dict]:
    rows = (
        db.query(MealCompletion)
        .filter(MealCompletion.user_id == user.id)
        .order_by(MealCompletion.meal_date.desc())
        .limit(limit_days * 4)
        .all()
    )
    by_date = defaultdict(lambda: {"completed": 0, "skipped": 0})
    for row in rows:
        key = row.meal_date
        if row.status == "completed":
            by_date[key]["completed"] += 1
        else:
            by_date[key]["skipped"] += 1

    return [
        {
            "meal_date": d,
            "completed_count": counts["completed"],
            "skipped_count": counts["skipped"],
            "total_count": counts["completed"] + counts["skipped"],
        }
        for d, counts in sorted(by_date.items(), reverse=True)
    ]


def get_today_nutrition_totals(db: Session, user: User) -> tuple[int, int]:
    today = date.today()
    plan = (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.plan_date == today)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )
    if plan is None:
        return 0, 0

    completed_types = {
        row.meal_type
        for row in db.query(MealCompletion).filter(
            MealCompletion.user_id == user.id,
            MealCompletion.meal_date == today,
            MealCompletion.status == "completed",
        )
    }
    if not completed_types:
        return 0, 0

    total_calories = sum(m["calories"] for m in plan.meals if m["meal_type"] in completed_types)
    total_protein = sum(m["protein_g"] for m in plan.meals if m["meal_type"] in completed_types)
    return total_calories, total_protein


def get_progress(db: Session, user: User) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    fitness_score, _basis = _compute_fitness_score(onboarding)

    weight_history = get_weight_history(db, user)
    workout_history = workout_service.get_history(db, user)
    nutrition_adherence = get_nutrition_adherence(db, user)
    streak = workout_service.compute_workout_streak(db, user)
    calories_today, protein_today = get_today_nutrition_totals(db, user)

    return {
        "weight_history": [{"log_date": w.log_date, "weight_kg": w.weight_kg} for w in weight_history],
        "workout_history": [{"workout_date": w.workout_date, "status": w.status} for w in workout_history],
        "nutrition_adherence": nutrition_adherence,
        "workout_streak_days": streak,
        "fitness_score": fitness_score,
        "recovery_trend": None,  # requires Module 4 daily check-ins
        "total_calories_logged_today": calories_today,
        "total_protein_logged_today": protein_today,
    }
