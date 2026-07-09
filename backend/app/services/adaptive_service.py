from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.adaptive_insight import AdaptiveInsight
from app.models.progress import WeightLog
from app.models.nutrition import MealCompletion
from app.services import (
    onboarding_service,
    medical_history_service,
    daily_checkin_service,
    workout_service,
    nutrition_service,
    notification_service,
    workout_preferences_service,
    nutrition_preferences_service,
)
from app.services.ai.adaptive_ai_service import generate_adaptive_analysis
from app.services.ai.adaptive_engine import compute_weight_trend
from app.services.ai.coach_ai_service import generate_coach_insight


def _get_nutrition_adherence_pct(db: Session, user: User, days: int = 14) -> float | None:
    """
    Reads MealCompletion directly rather than going through progress_service,
    to avoid a circular import (progress_service also depends on this module
    for recovery/recommendation history) — same pattern as _get_weight_history.
    """
    cutoff = date.today() - timedelta(days=days)
    rows = db.query(MealCompletion).filter(MealCompletion.user_id == user.id, MealCompletion.meal_date >= cutoff).all()
    if not rows:
        return None
    completed = sum(1 for r in rows if r.status == "completed")
    return round((completed / len(rows)) * 100)


def _get_weight_history(db: Session, user: User, limit: int = 30) -> list[dict]:
    """
    Reads WeightLog directly rather than going through progress_service, to
    avoid a circular import (progress_service also depends on this module
    for recovery/recommendation history).
    """
    rows = (
        db.query(WeightLog)
        .filter(WeightLog.user_id == user.id)
        .order_by(WeightLog.log_date.asc())
        .limit(limit)
        .all()
    )
    return [{"log_date": w.log_date.isoformat(), "weight_kg": w.weight_kg} for w in rows]


def _build_context(db: Session, user: User) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)

    recent_checkins = [
        {
            "checkin_date": c.checkin_date.isoformat(),
            "sleep_hours": c.sleep_hours,
            "energy_level": c.energy_level,
            "muscle_soreness": c.muscle_soreness,
            "pain_level": c.pain_level,
            "mood": c.mood,
            "water_intake_ml": c.water_intake_ml,
        }
        for c in daily_checkin_service.get_recent_checkins(db, user, days=7)
    ]

    recent_workouts = workout_service.get_history(db, user, limit=14)
    recent_workout_statuses = [w.status for w in recent_workouts]

    current_plan = workout_service.get_or_create_current_plan(db, user)
    scheduled_training_days = sum(1 for day in current_plan.schedule if not day["is_rest_day"])

    weight_history = _get_weight_history(db, user)
    nutrition_adherence_pct = _get_nutrition_adherence_pct(db, user)
    workout_streak_days = workout_service.compute_workout_streak(db, user)

    water_values = [c["water_intake_ml"] for c in recent_checkins if c["water_intake_ml"] is not None]
    recent_avg_water_ml = round(sum(water_values) / len(water_values)) if water_values else None

    nutrition_prefs = nutrition_preferences_service.get_or_create_preferences(db, user)
    body_metrics = onboarding.body_metrics or {}
    water_goal_ml = nutrition_prefs.water_goal_ml or (
        round(body_metrics["weight_kg"] * 35) if body_metrics.get("weight_kg") else None
    )

    workout_prefs = workout_preferences_service.get_or_create_preferences(db, user)

    return {
        "goals": onboarding.goals,
        "medical": {
            "injuries": (medical.injuries if medical else []) or [],
            "conditions": (medical.conditions if medical else []) or [],
        },
        "recent_checkins": recent_checkins,
        "recent_workout_statuses": recent_workout_statuses,
        "scheduled_training_days": scheduled_training_days,
        "weight_history": weight_history,
        "nutrition_adherence_pct": nutrition_adherence_pct,
        "workout_streak_days": workout_streak_days,
        "variety_seed": date.today().toordinal(),
        "preferences": {"workout_intensity": workout_prefs.workout_intensity},
        "recent_avg_water_ml": recent_avg_water_ml,
        "water_goal_ml": water_goal_ml,
    }


def generate_insight(db: Session, user: User, regenerate_plans: bool = True) -> AdaptiveInsight:
    context = _build_context(db, user)
    result = generate_adaptive_analysis(context)

    insight = AdaptiveInsight(
        user_id=user.id,
        recovery_score=result["recovery_score"],
        consistency_pct=result["consistency_pct"],
        fatigue_flag=result["fatigue_flag"],
        intensity_modifier=result["intensity_modifier"],
        nutrition_calorie_adjustment=result["nutrition_calorie_adjustment"],
        recommendations=result["recommendations"],
        analysis_basis={"context": context, "prompt": result["prompt"]},
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)

    if result["fatigue_flag"]:
        notification_service.create_notification(
            db, user, "workout_reminder", "Your recovery signals suggest taking it easier — today's plan has been adjusted."
        )

    if regenerate_plans:
        # Regenerated plans automatically pick up the new insight via
        # workout_service/nutrition_service's own latest-insight lookups.
        workout_service.regenerate_current_plan(db, user)
        nutrition_service.regenerate_today_plan(db, user)

    return insight


def get_latest_insight(db: Session, user: User) -> AdaptiveInsight | None:
    return (
        db.query(AdaptiveInsight)
        .filter(AdaptiveInsight.user_id == user.id)
        .order_by(AdaptiveInsight.created_at.desc())
        .first()
    )


def get_or_create_latest_insight(db: Session, user: User) -> AdaptiveInsight:
    """Used by the dashboard: don't force a plan regeneration just to display a recovery score."""
    insight = get_latest_insight(db, user)
    if insight is None:
        insight = generate_insight(db, user, regenerate_plans=False)
    return insight


def get_insight_history(db: Session, user: User, limit: int = 30) -> list[AdaptiveInsight]:
    return (
        db.query(AdaptiveInsight)
        .filter(AdaptiveInsight.user_id == user.id)
        .order_by(AdaptiveInsight.created_at.desc())
        .limit(limit)
        .all()
    )


def generate_coach_tip(db: Session, user: User) -> str:
    """
    The Dashboard's "AI Coach" tip: one short, personalized sentence combining
    recovery, adherence, streak, and weight trend — replacing the old
    onboarding-only placeholder. Cheap: doesn't create a new AdaptiveInsight
    or regenerate any plans, just reads what already exists.
    """
    onboarding = onboarding_service.get_onboarding(db, user)
    if not onboarding.goals:
        return generate_coach_insight({"has_onboarding": False})["tip"]

    latest_insight = get_latest_insight(db, user)
    weight_history = _get_weight_history(db, user)
    primary_goal = (onboarding.goals or {}).get("primary_goal")

    context = {
        "has_onboarding": True,
        "goals": onboarding.goals,
        "recovery_score": latest_insight.recovery_score if latest_insight else None,
        "consistency_pct": latest_insight.consistency_pct if latest_insight else None,
        "fatigue_flag": latest_insight.fatigue_flag if latest_insight else False,
        "nutrition_adherence_pct": _get_nutrition_adherence_pct(db, user),
        "workout_streak_days": workout_service.compute_workout_streak(db, user),
        "weight_trend": compute_weight_trend(weight_history, primary_goal),
        "variety_seed": date.today().toordinal(),
    }
    return generate_coach_insight(context)["tip"]
