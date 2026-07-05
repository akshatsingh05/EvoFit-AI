from datetime import date

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.nutrition import NutritionPlan, MealCompletion
from app.models.adaptive_insight import AdaptiveInsight
from app.services import onboarding_service, medical_history_service, notification_service
from app.services.ai.nutrition_ai_service import generate_nutrition_targets


def _latest_calorie_adjustment(db: Session, user: User) -> float:
    """Pulls the most recent adaptive analysis so regenerated plans reflect it automatically."""
    insight = (
        db.query(AdaptiveInsight)
        .filter(AdaptiveInsight.user_id == user.id)
        .order_by(AdaptiveInsight.created_at.desc())
        .first()
    )
    return insight.nutrition_calorie_adjustment if insight else 0.0


def _build_context(db: Session, user: User) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)
    return {
        "goals": onboarding.goals,
        "body_metrics": onboarding.body_metrics,
        "lifestyle_diet": onboarding.lifestyle_diet,
        "workouts_per_week": (onboarding.fitness_experience or {}).get("workouts_per_week_current", 0),
        "medical": {
            "allergies": medical.allergies if medical else None,
        },
        "adaptive_calorie_adjustment": _latest_calorie_adjustment(db, user),
    }


def _generate_and_store(db: Session, user: User, plan_date: date) -> NutritionPlan:
    context = _build_context(db, user)
    result = generate_nutrition_targets(context)
    plan = NutritionPlan(
        user_id=user.id,
        plan_date=plan_date,
        target_calories=result["target_calories"],
        target_protein_g=result["target_protein_g"],
        target_carbs_g=result["target_carbs_g"],
        target_fat_g=result["target_fat_g"],
        water_goal_ml=result["water_goal_ml"],
        meals=result["meals"],
        generation_basis={"context": context, "prompt": result["prompt"]},
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_or_create_today_plan(db: Session, user: User) -> NutritionPlan:
    today = date.today()
    plan = (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.plan_date == today)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )
    if plan is None:
        plan = _generate_and_store(db, user, today)
    return plan


def regenerate_today_plan(db: Session, user: User) -> NutritionPlan:
    return _generate_and_store(db, user, date.today())


def record_meal_completion(db: Session, user: User, meal_date: date, meal_type: str, status: str) -> MealCompletion:
    if status not in ("completed", "skipped"):
        raise ValueError("status must be 'completed' or 'skipped'")

    plan = get_or_create_today_plan(db, user) if meal_date == date.today() else None

    existing = (
        db.query(MealCompletion)
        .filter(
            MealCompletion.user_id == user.id,
            MealCompletion.meal_date == meal_date,
            MealCompletion.meal_type == meal_type,
        )
        .first()
    )
    if existing:
        existing.status = status
        db.commit()
        db.refresh(existing)
        return existing

    record = MealCompletion(
        user_id=user.id,
        plan_id=plan.id if plan else get_or_create_today_plan(db, user).id,
        meal_date=meal_date,
        meal_type=meal_type,
        status=status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_completions_for_date(db: Session, user: User, meal_date: date) -> dict[str, str]:
    rows = (
        db.query(MealCompletion)
        .filter(MealCompletion.user_id == user.id, MealCompletion.meal_date == meal_date)
        .all()
    )
    return {row.meal_type: row.status for row in rows}


def get_history(db: Session, user: User, limit: int = 60) -> list[MealCompletion]:
    return (
        db.query(MealCompletion)
        .filter(MealCompletion.user_id == user.id)
        .order_by(MealCompletion.meal_date.desc())
        .limit(limit)
        .all()
    )


def get_today_plan_if_exists(db: Session, user: User) -> NutritionPlan | None:
    today = date.today()
    return (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.plan_date == today)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )
