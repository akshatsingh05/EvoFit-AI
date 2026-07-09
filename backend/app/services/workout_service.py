from datetime import date, timedelta
import uuid

from sqlalchemy.orm import Session

from app.data.exercise_library import exercises_for, find_exercise_by_name
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutCompletion
from app.models.adaptive_insight import AdaptiveInsight
from app.services import onboarding_service, medical_history_service, notification_service, week_utils
from app.services import workout_preferences_service
from app.services.ai.workout_ai_service import generate_workout_schedule


_week_start = week_utils.week_start
week_start_for_offset = week_utils.week_start_for_offset
get_registration_week_start = week_utils.get_registration_week_start
is_week_before_registration = week_utils.is_week_before_registration


def _latest_intensity_modifier(db: Session, user: User) -> int:
    """Pulls the most recent adaptive analysis so regenerated plans reflect it automatically."""
    insight = (
        db.query(AdaptiveInsight)
        .filter(AdaptiveInsight.user_id == user.id)
        .order_by(AdaptiveInsight.created_at.desc())
        .first()
    )
    return insight.intensity_modifier if insight else 0


def _exercise_names_in_plan(plan: WorkoutPlan | None) -> list[str]:
    if plan is None:
        return []
    return [ex["name"] for day in plan.schedule for ex in day.get("exercises", [])]


def _preferences_context(db: Session, user: User) -> dict:
    """Sprint 4: shapes WorkoutPreferences into the plain-dict context the
    generator expects, including the reduced (dominant-only) replacement
    memory — see workout_preferences_service.dominant_replacements."""
    prefs = workout_preferences_service.get_or_create_preferences(db, user)
    return {
        "workout_style": prefs.workout_style,
        "workout_location": prefs.workout_location,
        "equipment_available": prefs.equipment_available or [],
        "preferred_duration_minutes": prefs.preferred_duration_minutes,
        "workout_intensity": prefs.workout_intensity,
        "preferred_workout_time": prefs.preferred_workout_time,
        "favorite_muscle_groups": prefs.favorite_muscle_groups or [],
        "liked_exercises": prefs.liked_exercises or [],
        "disliked_exercises": prefs.disliked_exercises or [],
        "avoid_movements": prefs.avoid_movements or [],
        "dominant_replacements": workout_preferences_service.dominant_replacements(prefs.exercise_replacement_memory),
    }


def _build_context(db: Session, user: User, variation_seed: str, avoid_exercise_names: list[str]) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)
    return {
        "goals": onboarding.goals,
        "fitness_experience": onboarding.fitness_experience,
        "body_metrics": onboarding.body_metrics,
        "medical": {
            "injuries": (medical.injuries if medical else []) or [],
            "conditions": (medical.conditions if medical else []) or [],
            "cleared_for_exercise": medical.cleared_for_exercise if medical else True,
        },
        "preferences": _preferences_context(db, user),
        "intensity_modifier": _latest_intensity_modifier(db, user),
        "variation_seed": variation_seed,
        "avoid_exercise_names": avoid_exercise_names,
    }


def _generate_and_store(
    db: Session, user: User, week_start_date: date, variation_seed: str, avoid_exercise_names: list[str]
) -> WorkoutPlan:
    context = _build_context(db, user, variation_seed, avoid_exercise_names)
    result = generate_workout_schedule(context)
    plan = WorkoutPlan(
        user_id=user.id,
        week_start_date=week_start_date,
        schedule=result["schedule"],
        generation_basis={"context": context, "prompt": result["prompt"], "bmi": result.get("bmi")},
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def _latest_plan_for_week(db: Session, user: User, week_start_date: date) -> WorkoutPlan | None:
    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date == week_start_date)
        .order_by(WorkoutPlan.created_at.desc())
        .first()
    )


def _adjacent_plan_for_avoidance(db: Session, user: User, week_start_date: date) -> WorkoutPlan | None:
    """The most recent plan from an earlier week, used only to seed exercise variety."""
    return (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date < week_start_date)
        .order_by(WorkoutPlan.week_start_date.desc())
        .first()
    )


def get_plan_for_week(db: Session, user: User, week_start_date: date) -> WorkoutPlan | None:
    """
    Fetches the plan for an arbitrary week, generating one if missing —
    unless the week falls entirely before the user registered, in which case
    `None` is returned so the caller can show a "no plan existed yet" state.
    Stable per user+week: repeated calls for the same week never change it;
    only `regenerate_plan_for_week` creates a new version.
    """
    plan = _latest_plan_for_week(db, user, week_start_date)
    if plan is not None:
        return plan

    if is_week_before_registration(week_start_date, user):
        return None

    previous_plan = _adjacent_plan_for_avoidance(db, user, week_start_date)
    seed = f"{user.id}:{week_start_date.isoformat()}"
    return _generate_and_store(db, user, week_start_date, seed, _exercise_names_in_plan(previous_plan))


def regenerate_plan_for_week(db: Session, user: User, week_start_date: date) -> WorkoutPlan:
    if is_week_before_registration(week_start_date, user) and _latest_plan_for_week(db, user, week_start_date) is None:
        raise ValueError("Cannot regenerate a plan for a week before the user's registration date")

    current_plan = _latest_plan_for_week(db, user, week_start_date)
    # Fresh nonce each call so regenerating twice in a row still gives
    # different results, and explicitly avoid whatever's in the plan being replaced.
    seed = f"{user.id}:{week_start_date.isoformat()}:{uuid.uuid4().hex}"
    return _generate_and_store(db, user, week_start_date, seed, _exercise_names_in_plan(current_plan))


def get_or_create_current_plan(db: Session, user: User) -> WorkoutPlan:
    """Kept for Dashboard/Adaptive/Progress, which only ever care about 'this week'."""
    return get_plan_for_week(db, user, _week_start(date.today()))


def regenerate_current_plan(db: Session, user: User) -> WorkoutPlan:
    return regenerate_plan_for_week(db, user, _week_start(date.today()))


def build_plan_info(db: Session, user: User, plan: WorkoutPlan) -> dict:
    """Data for the Plan Information card: why this plan looks the way it does."""
    all_versions = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date == plan.week_start_date)
        .order_by(WorkoutPlan.created_at.asc())
        .all()
    )
    context = (plan.generation_basis or {}).get("context", {})
    goals = context.get("goals") or {}
    fitness_experience = context.get("fitness_experience") or {}
    workout_days = sum(1 for day in plan.schedule if not day.get("is_rest_day"))

    return {
        "generated_on": all_versions[0].created_at if all_versions else plan.created_at,
        "current_goal": goals.get("primary_goal"),
        "difficulty": fitness_experience.get("experience_level"),
        "workout_days": workout_days,
        "plan_version": len(all_versions) or 1,
        "last_regenerated_at": plan.created_at if len(all_versions) > 1 else None,
    }


def list_workout_weeks_history(db: Session, user: User, limit: int = 12) -> list[WorkoutPlan]:
    """One (latest) plan per past week, most recent first — the Workout History list."""
    current_week = _week_start(date.today())
    rows = (
        db.query(WorkoutPlan)
        .filter(WorkoutPlan.user_id == user.id, WorkoutPlan.week_start_date < current_week)
        .order_by(WorkoutPlan.week_start_date.desc(), WorkoutPlan.created_at.desc())
        .all()
    )
    seen_weeks = set()
    history: list[WorkoutPlan] = []
    for row in rows:
        if row.week_start_date in seen_weeks:
            continue
        seen_weeks.add(row.week_start_date)
        history.append(row)
        if len(history) >= limit:
            break
    return history


def get_workout_history_entries(db: Session, user: User, limit: int = 12) -> list[dict]:
    """Adapts weekly WorkoutPlans into the shared HistoryEntry shape (see schemas/history.py)."""
    entries = []
    for plan in list_workout_weeks_history(db, user, limit):
        completions = get_completions_for_plan(db, user, plan)
        completed = sum(1 for status in completions.values() if status == "completed")
        active_days = sum(1 for day in plan.schedule if not day.get("is_rest_day"))
        week_end = plan.week_start_date + timedelta(days=6)
        entries.append(
            {
                "period_start": plan.week_start_date,
                "period_end": week_end,
                "title": f"Week of {plan.week_start_date.strftime('%b %d').replace(' 0', ' ')}",
                "summary": f"{active_days} workout days · {completed} completed",
                "created_at": plan.created_at,
                "detail_ref": plan.week_start_date.isoformat(),
            }
        )
    return entries


def get_calendar_data(db: Session, user: User, start_date: date, end_date: date) -> list[dict]:
    """
    Builds a per-day status list for the Workout Calendar view. Weeks are
    fetched (and generated, per the same registration-date rule as week nav)
    once per distinct week in the range, not once per day.
    """
    today = date.today()
    week_cache: dict[date, WorkoutPlan | None] = {}
    completions_cache: dict[date, dict[str, str]] = {}
    days = []

    cursor = start_date
    while cursor <= end_date:
        week_start = _week_start(cursor)
        if week_start not in week_cache:
            week_cache[week_start] = get_plan_for_week(db, user, week_start)
            if week_cache[week_start] is not None:
                completions_cache[week_start] = get_completions_for_plan(db, user, week_cache[week_start])

        plan = week_cache[week_start]
        if plan is None:
            days.append({"date": cursor, "status": "no_plan", "workout": None})
            cursor += timedelta(days=1)
            continue

        day = plan.schedule[cursor.weekday()]
        if day.get("is_rest_day"):
            days.append({"date": cursor, "status": "rest", "workout": None})
            cursor += timedelta(days=1)
            continue

        completion_status = completions_cache[week_start].get(cursor.isoformat())
        if completion_status == "completed":
            status = "completed"
        elif completion_status == "skipped":
            status = "skipped"
        elif cursor > today:
            status = "upcoming"
        elif cursor == today:
            status = "upcoming"  # today, not yet logged
        else:
            status = "missed"  # past day, non-rest, never logged

        days.append(
            {
                "date": cursor,
                "status": status,
                "workout": {
                    "focus": day.get("focus"),
                    "exercises": day.get("exercises", []),
                    "duration_minutes": day.get("estimated_duration_minutes", 0),
                    "completion_status": completion_status,
                },
            }
        )
        cursor += timedelta(days=1)

    return days


def get_completions_for_week(db: Session, user: User, plan: WorkoutPlan | None) -> dict[str, str]:
    """Thin alias kept explicit for the week-nav completions endpoint; `plan` may be None
    (week before registration), in which case there's nothing to look up."""
    if plan is None:
        return {}
    return get_completions_for_plan(db, user, plan)


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
    return _latest_plan_for_week(db, user, _week_start(date.today()))


# --- Sprint 4: Plan Customization (objective 4) + Preference Memory (objective 5) ---


def get_exercise_alternatives(db: Session, user: User, plan: WorkoutPlan, day_index: int, exercise_index: int) -> list[str]:
    """
    Alternatives for the "Replace Exercise" flow: other exercises matching
    the same day's focus, honoring the user's current equipment/injury/
    dislike constraints, excluding exercises already scheduled that day so a
    replacement never duplicates a sibling exercise.
    """
    if day_index < 0 or day_index >= len(plan.schedule):
        raise ValueError("day_index out of range")
    day = plan.schedule[day_index]
    if exercise_index < 0 or exercise_index >= len(day.get("exercises", [])):
        raise ValueError("exercise_index out of range")

    context = (plan.generation_basis or {}).get("context", {})
    medical = context.get("medical") or {}
    fitness = context.get("fitness_experience") or {}
    preferences = context.get("preferences") or {}

    from app.services.ai.workout_generator import (
        _equipment_tags_from_preferences,
        _parse_avoid_movements,
        _pool_with_fallback,
    )

    injuries = set(medical.get("injuries") or [])
    avoid_injury_tags, avoid_name_keywords = _parse_avoid_movements(preferences.get("avoid_movements") or [])
    conditions = set(medical.get("conditions") or [])
    equipment_tags = _equipment_tags_from_preferences(preferences.get("equipment_available") or [])
    disliked = set(preferences.get("disliked_exercises") or [])
    already_in_day = {ex["name"] for ex in day["exercises"]}
    equipment_access = fitness.get("equipment_access", "none")

    pool = _pool_with_fallback(
        day["focus"], equipment_access, injuries, avoid_injury_tags, conditions, False,
        equipment_tags, disliked | already_in_day, avoid_name_keywords,
    )
    if not pool and day["focus"] != "full_body":
        pool = _pool_with_fallback(
            "full_body", equipment_access, injuries, avoid_injury_tags, conditions, False,
            equipment_tags, disliked | already_in_day, avoid_name_keywords,
        )
    return [ex["name"] for ex in pool]


def replace_exercise_in_plan(
    db: Session, user: User, plan: WorkoutPlan, day_index: int, exercise_index: int, replacement_name: str | None
) -> WorkoutPlan:
    """
    Sprint 4 objective 4: swaps a single exercise in place, preserving the
    day's overall structure (sets/reps/rest, position, sibling exercises).
    If `replacement_name` isn't provided, one is picked at random from the
    valid alternatives ("Swap Exercise"). Also records the replacement in
    Workout Preferences (objective 5) so a repeated choice gets favored
    automatically in future generations.
    """
    if day_index < 0 or day_index >= len(plan.schedule):
        raise ValueError("day_index out of range")
    day = plan.schedule[day_index]
    if exercise_index < 0 or exercise_index >= len(day.get("exercises", [])):
        raise ValueError("exercise_index out of range")
    original = day["exercises"][exercise_index]

    alternatives = get_exercise_alternatives(db, user, plan, day_index, exercise_index)
    if not alternatives:
        raise ValueError("No valid alternative exercises are available for this slot")

    if replacement_name is None:
        import random
        replacement_name = random.choice(alternatives)
    elif replacement_name not in alternatives:
        raise ValueError("That exercise isn't a valid alternative for this slot")

    replacement_exercise = find_exercise_by_name(replacement_name)
    if replacement_exercise is None:
        raise ValueError("Unknown exercise")

    new_schedule = [dict(d) for d in plan.schedule]
    new_exercises = list(new_schedule[day_index]["exercises"])
    new_exercises[exercise_index] = {
        "name": replacement_exercise["name"],
        "sets": original["sets"],
        "reps": original["reps"],
        "rest_seconds": original["rest_seconds"],
        "instructions": replacement_exercise["instructions"],
    }
    new_schedule[day_index] = {**new_schedule[day_index], "exercises": new_exercises}
    plan.schedule = new_schedule
    db.commit()
    db.refresh(plan)

    workout_preferences_service.record_exercise_replacement(db, user, original["name"], replacement_exercise["name"])

    return plan
