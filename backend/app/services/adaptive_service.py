from sqlalchemy.orm import Session

from app.models.user import User
from app.models.adaptive_insight import AdaptiveInsight
from app.models.progress import WeightLog
from app.services import (
    onboarding_service,
    medical_history_service,
    daily_checkin_service,
    workout_service,
    nutrition_service,
    notification_service,
)
from app.services.ai.adaptive_ai_service import generate_adaptive_analysis


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
        }
        for c in daily_checkin_service.get_recent_checkins(db, user, days=7)
    ]

    recent_workouts = workout_service.get_history(db, user, limit=14)
    recent_workout_statuses = [w.status for w in recent_workouts]

    current_plan = workout_service.get_or_create_current_plan(db, user)
    scheduled_training_days = sum(1 for day in current_plan.schedule if not day["is_rest_day"])

    weight_history = _get_weight_history(db, user)

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
