from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutCompletion
from app.services import onboarding_service, medical_history_service, notification_service
from app.services.ai.workout_ai_service import generate_workout_schedule


def _week_start(for_date: date) -> date:
    return for_date - timedelta(days=for_date.weekday())


def _build_context(db: Session, user: User) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)
    return {
        "goals": onboarding.goals,
        "fitness_experience": onboarding.fitness_experience,
        "medical": {
            "injuries": (medical.injuries if medical else []) or [],
            "conditions": (medical.conditions if medical else []) or [],
        },
    }


def _generate_and_store(db: Session, user: User, week_start_date: date) -> WorkoutPlan:
    context = _build_context(db, user)
    result = generate_workout_schedule(context)
    plan = WorkoutPlan(
        user_id=user.id,
        week_start_date=week_start_date,
        schedule=result["schedule"],
        generation_basis={"context": context, "prompt": result["prompt"]},
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def get_or_create_current_plan(db: Session, user: User) -> WorkoutPlan:
    week_start_date = _week_start(date.today())
    plan = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date == week_start_date)
        .order_by(WorkoutPlan.created_at.desc())
        .first()
    )
    if plan is None:
        plan = _generate_and_store(db, user, week_start_date)
    return plan


def regenerate_current_plan(db: Session, user: User) -> WorkoutPlan:
    week_start_date = _week_start(date.today())
    return _generate_and_store(db, user, week_start_date)


def get_completions_for_plan(db: Session, user: User, plan: WorkoutPlan) -> dict[str, str]:
    start = plan.week_start_date
    end = start + timedelta(days=6)
    rows = (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.user_id == user.id, WorkoutCompletion.workout_date.between(start, end))
        .all()
    )
    return {row.workout_date.isoformat(): row.status for row in rows}


def record_completion(db: Session, user: User, workout_date: date, status: str) -> WorkoutCompletion:
    if status not in ("completed", "skipped"):
        raise ValueError("status must be 'completed' or 'skipped'")

    plan = get_or_create_current_plan(db, user)

    existing = (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.user_id == user.id, WorkoutCompletion.workout_date == workout_date)
        .first()
    )
    if existing:
        existing.status = status
        db.commit()
        db.refresh(existing)
        record = existing
    else:
        record = WorkoutCompletion(user_id=user.id, plan_id=plan.id, workout_date=workout_date, status=status)
        db.add(record)
        db.commit()
        db.refresh(record)

    if status == "completed":
        notification_service.create_notification(
            db, user, "workout_completed", f"Nice work — you completed your {workout_date.strftime('%A')} workout."
        )
        streak = compute_workout_streak(db, user)
        if streak in (7, 30, 100):
            notification_service.create_notification(
                db, user, "goal_achieved", f"You've hit a {streak}-day workout streak. Keep it up!"
            )

    return record


def compute_workout_streak(db: Session, user: User) -> int:
    completions = (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.user_id == user.id)
        .order_by(WorkoutCompletion.workout_date.desc())
        .all()
    )
    comp_map = {c.workout_date: c.status for c in completions}

    streak = 0
    cursor = date.today()
    while True:
        status = comp_map.get(cursor)
        if status == "completed":
            streak += 1
            cursor -= timedelta(days=1)
        elif status == "skipped":
            break
        elif cursor not in comp_map and cursor == date.today():
            cursor -= timedelta(days=1)  # today not logged yet — don't penalize, check yesterday
        else:
            break
    return streak


def get_history(db: Session, user: User, limit: int = 60) -> list[WorkoutCompletion]:
    return (
        db.query(WorkoutCompletion)
        .filter(WorkoutCompletion.user_id == user.id)
        .order_by(WorkoutCompletion.workout_date.desc())
        .limit(limit)
        .all()
    )


def get_current_plan_if_exists(db: Session, user: User) -> WorkoutPlan | None:
    week_start_date = _week_start(date.today())
    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date == week_start_date)
        .order_by(WorkoutPlan.created_at.desc())
        .first()
    )
