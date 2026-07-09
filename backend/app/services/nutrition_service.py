from dataclasses import dataclass
from datetime import date, datetime, timedelta
import uuid

from sqlalchemy.orm import Session

from app.data.meal_library import meals_for, find_meal_by_name, pool_key_for_slot, PREFERENCE_DIET_TYPE_MAP
from app.models.user import User
from app.models.nutrition import NutritionPlan, MealCompletion
from app.models.adaptive_insight import AdaptiveInsight
from app.services import onboarding_service, medical_history_service, notification_service, week_utils
from app.services import nutrition_preferences_service
from app.services.ai.nutrition_ai_service import generate_nutrition_targets

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Re-exported for router convenience (single source of truth lives in week_utils,
# shared with workout_service — see Sprint 2 architecture notes).
week_start_for_offset = week_utils.week_start_for_offset
get_registration_week_start = week_utils.get_registration_week_start
is_week_before_registration = week_utils.is_week_before_registration


@dataclass
class TodayNutritionView:
    """
    Adapts a single day out of a weekly NutritionPlan into the flat shape
    Dashboard/Adaptive/Progress/the existing `/nutrition` router already
    expect (id, target_calories, ..., meals, created_at) — so none of those
    call sites need to know NutritionPlan became weekly in Sprint 2.
    """

    id: str
    week_start_date: date
    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int
    water_goal_ml: int
    meals: list
    created_at: datetime


def _latest_calorie_adjustment(db: Session, user: User) -> float:
    """Pulls the most recent adaptive analysis so regenerated plans reflect it automatically."""
    insight = (
        db.query(AdaptiveInsight)
        .filter(AdaptiveInsight.user_id == user.id)
        .order_by(AdaptiveInsight.created_at.desc())
        .first()
    )
    return insight.nutrition_calorie_adjustment if insight else 0.0


def _meal_names_in_day(day: dict) -> list[str]:
    return [m["name"] for m in day.get("meals", [])]


def _meal_names_in_plan(plan: NutritionPlan | None) -> list[str]:
    if plan is None:
        return []
    names: list[str] = []
    for day in plan.days:
        names.extend(_meal_names_in_day(day))
    return names


def get_day_from_plan(plan: NutritionPlan | None, target_date: date) -> dict | None:
    """The reusable bridge from weekly storage to a single day's targets/meals.
    Used by the router, Dashboard (via TodayNutritionView), Progress, and Reports."""
    if plan is None:
        return None
    target_iso = target_date.isoformat()
    return next((d for d in plan.days if d.get("date") == target_iso), None)


def _preferences_context(db: Session, user: User) -> dict:
    """Sprint 4: shapes NutritionPreferences into the plain-dict context the
    generator expects, including reduced (dominant-only) replacement memory."""
    prefs = nutrition_preferences_service.get_or_create_preferences(db, user)
    return {
        "diet_type": prefs.diet_type,
        "cuisine_preference": prefs.cuisine_preference,
        "budget": prefs.budget,
        "meals_per_day": prefs.meals_per_day,
        "favorite_foods": prefs.favorite_foods or [],
        "disliked_foods": prefs.disliked_foods or [],
        "allergies": prefs.allergies or [],
        "water_goal_ml": prefs.water_goal_ml,
        "preferred_snacks": prefs.preferred_snacks or [],
        "cooking_time_preference": prefs.cooking_time_preference,
        "dominant_replacements": nutrition_preferences_service.dominant_replacements(prefs.meal_replacement_memory),
    }


def _build_base_context(db: Session, user: User) -> dict:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)
    return {
        "goals": onboarding.goals,
        "body_metrics": onboarding.body_metrics,
        "lifestyle_diet": onboarding.lifestyle_diet,
        "workouts_per_week": (onboarding.fitness_experience or {}).get("workouts_per_week_current", 0),
        "medical": {
            "allergies": medical.allergies if medical else None,
            "conditions": (medical.conditions if medical else []) or [],
        },
        "preferences": _preferences_context(db, user),
    }


def _generate_week_and_store(
    db: Session, user: User, week_start_date: date, seed_suffix: str, avoid_meal_names_seed: list[str]
) -> NutritionPlan:
    """Generates all 7 days by calling the existing (untouched) Sprint 1 AI
    generator once per day, carrying forward an accumulating avoid-list so
    meals vary both within the week and from the previous week/version."""
    base_context = _build_base_context(db, user)
    calorie_adjustment = _latest_calorie_adjustment(db, user)

    days = []
    day_bases = []
    running_avoid = list(avoid_meal_names_seed)

    for i, day_name in enumerate(DAY_NAMES):
        day_date = week_start_date + timedelta(days=i)
        variation_seed = f"{user.id}:{week_start_date.isoformat()}:{day_name}:{seed_suffix}"
        context = {
            **base_context,
            "adaptive_calorie_adjustment": calorie_adjustment,
            "variation_seed": variation_seed,
            "avoid_meal_names": running_avoid,
        }
        result = generate_nutrition_targets(context)
        day_obj = {
            "day_name": day_name,
            "date": day_date.isoformat(),
            "target_calories": result["target_calories"],
            "target_protein_g": result["target_protein_g"],
            "target_carbs_g": result["target_carbs_g"],
            "target_fat_g": result["target_fat_g"],
            "water_goal_ml": result["water_goal_ml"],
            "meals": result["meals"],
        }
        days.append(day_obj)
        day_bases.append({"day_name": day_name, "prompt": result["prompt"], "bmi": result.get("bmi")})
        running_avoid = running_avoid + _meal_names_in_day(day_obj)

    plan = NutritionPlan(
        user_id=user.id,
        week_start_date=week_start_date,
        days=days,
        generation_basis={"context": base_context, "adaptive_calorie_adjustment": calorie_adjustment, "days": day_bases},
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def _latest_plan_for_week(db: Session, user: User, week_start_date: date) -> NutritionPlan | None:
    return (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.week_start_date == week_start_date)
        .order_by(NutritionPlan.created_at.desc())
        .first()
    )


def _adjacent_plan_for_avoidance(db: Session, user: User, week_start_date: date) -> NutritionPlan | None:
    return (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.week_start_date < week_start_date)
        .order_by(NutritionPlan.week_start_date.desc())
        .first()
    )


def get_plan_for_week(db: Session, user: User, week_start_date: date) -> NutritionPlan | None:
    """Mirrors workout_service.get_plan_for_week exactly. `None` means the
    week is before the user's registration date and was never generated."""
    plan = _latest_plan_for_week(db, user, week_start_date)
    if plan is not None:
        return plan

    if week_utils.is_week_before_registration(week_start_date, user):
        return None

    previous_plan = _adjacent_plan_for_avoidance(db, user, week_start_date)
    return _generate_week_and_store(db, user, week_start_date, "initial", _meal_names_in_plan(previous_plan))


def regenerate_plan_for_week(db: Session, user: User, week_start_date: date) -> NutritionPlan:
    if week_utils.is_week_before_registration(week_start_date, user) and _latest_plan_for_week(db, user, week_start_date) is None:
        raise ValueError("Cannot regenerate a plan for a week before the user's registration date")

    current_plan = _latest_plan_for_week(db, user, week_start_date)
    nonce = uuid.uuid4().hex
    return _generate_week_and_store(db, user, week_start_date, nonce, _meal_names_in_plan(current_plan))


def build_plan_info(db: Session, user: User, plan: NutritionPlan) -> dict:
    """Data for the Plan Information card, mirroring workout_service.build_plan_info."""
    all_versions = (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.week_start_date == plan.week_start_date)
        .order_by(NutritionPlan.created_at.asc())
        .all()
    )
    context = (plan.generation_basis or {}).get("context", {})
    goals = context.get("goals") or {}
    avg_calories = round(sum(d["target_calories"] for d in plan.days) / len(plan.days)) if plan.days else None

    return {
        "generated_on": all_versions[0].created_at if all_versions else plan.created_at,
        "current_goal": goals.get("primary_goal"),
        "difficulty": None,
        "calories_target": avg_calories,
        "plan_version": len(all_versions) or 1,
        "last_regenerated_at": plan.created_at if len(all_versions) > 1 else None,
    }


def list_nutrition_weeks_history(db: Session, user: User, limit: int = 12) -> list[NutritionPlan]:
    current_week = week_utils.week_start(date.today())
    rows = (
        db.query(NutritionPlan)
        .filter(NutritionPlan.user_id == user.id, NutritionPlan.week_start_date < current_week)
        .order_by(NutritionPlan.week_start_date.desc(), NutritionPlan.created_at.desc())
        .all()
    )
    seen_weeks = set()
    history: list[NutritionPlan] = []
    for row in rows:
        if row.week_start_date in seen_weeks:
            continue
        seen_weeks.add(row.week_start_date)
        history.append(row)
        if len(history) >= limit:
            break
    return history


def get_nutrition_history_entries(db: Session, user: User, limit: int = 12) -> list[dict]:
    """Adapts weekly NutritionPlans into the shared HistoryEntry shape (see schemas/history.py)."""
    entries = []
    for plan in list_nutrition_weeks_history(db, user, limit):
        week_end = plan.week_start_date + timedelta(days=6)
        avg_calories = round(sum(d["target_calories"] for d in plan.days) / len(plan.days)) if plan.days else 0
        completed_meals = (
            db.query(MealCompletion)
            .filter(
                MealCompletion.user_id == user.id,
                MealCompletion.meal_date.between(plan.week_start_date, week_end),
                MealCompletion.status == "completed",
            )
            .count()
        )
        entries.append(
            {
                "period_start": plan.week_start_date,
                "period_end": week_end,
                "title": f"Week of {plan.week_start_date.strftime('%b %d').replace(' 0', ' ')}",
                "summary": f"Avg {avg_calories} kcal/day · {completed_meals} meals logged",
                "created_at": plan.created_at,
                "detail_ref": plan.week_start_date.isoformat(),
            }
        )
    return entries


# --- Backward-compatible "today" entry points used by Dashboard/Adaptive/Progress ---


def _today_view(week_plan: NutritionPlan | None, target_date: date) -> TodayNutritionView | None:
    if week_plan is None:
        return None
    day = get_day_from_plan(week_plan, target_date)
    if day is None:
        return None
    return TodayNutritionView(
        id=week_plan.id,
        week_start_date=week_plan.week_start_date,
        target_calories=day["target_calories"],
        target_protein_g=day["target_protein_g"],
        target_carbs_g=day["target_carbs_g"],
        target_fat_g=day["target_fat_g"],
        water_goal_ml=day["water_goal_ml"],
        meals=day["meals"],
        created_at=week_plan.created_at,
    )


def get_or_create_today_plan(db: Session, user: User) -> TodayNutritionView:
    week_plan = get_plan_for_week(db, user, week_utils.week_start(date.today()))
    return _today_view(week_plan, date.today())


def regenerate_today_plan(db: Session, user: User) -> TodayNutritionView:
    week_plan = regenerate_plan_for_week(db, user, week_utils.week_start(date.today()))
    return _today_view(week_plan, date.today())


def get_today_plan_if_exists(db: Session, user: User) -> TodayNutritionView | None:
    week_plan = _latest_plan_for_week(db, user, week_utils.week_start(date.today()))
    return _today_view(week_plan, date.today())


def record_meal_completion(db: Session, user: User, meal_date: date, meal_type: str, status: str) -> MealCompletion:
    if status not in ("completed", "skipped"):
        raise ValueError("status must be 'completed' or 'skipped'")

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

    plan = get_plan_for_week(db, user, week_utils.week_start(meal_date))
    if plan is None:
        raise ValueError("No nutrition plan exists for that date")

    record = MealCompletion(user_id=user.id, plan_id=plan.id, meal_date=meal_date, meal_type=meal_type, status=status)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_completions_for_week(db: Session, user: User, week_start_date: date) -> dict[str, dict[str, str]]:
    week_end = week_start_date + timedelta(days=6)
    rows = (
        db.query(MealCompletion)
        .filter(MealCompletion.user_id == user.id, MealCompletion.meal_date.between(week_start_date, week_end))
        .all()
    )
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        result.setdefault(row.meal_date.isoformat(), {})[row.meal_type] = row.status
    return result


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


# --- Sprint 4: Plan Customization (objective 4) + Preference Memory (objective 5) ---


def _scale_meal(meal: dict, target_calories: float) -> dict:
    factor = target_calories / meal["calories"] if meal["calories"] else 1
    return {
        "name": meal["name"],
        "calories": round(meal["calories"] * factor),
        "protein_g": round(meal["protein_g"] * factor),
        "carbs_g": round(meal["carbs_g"] * factor),
        "fat_g": round(meal["fat_g"] * factor),
    }


def get_meal_alternatives(db: Session, user: User, plan: NutritionPlan, day_index: int, meal_type: str) -> list[str]:
    """Alternatives for the "Replace Meal" flow: other meals for the same
    slot honoring diet type, allergens, and disliked foods, excluding meals
    already scheduled that day."""
    if day_index < 0 or day_index >= len(plan.days):
        raise ValueError("day_index out of range")
    day = plan.days[day_index]
    if meal_type not in {m["meal_type"] for m in day.get("meals", [])}:
        raise ValueError("meal_type not found on this day")

    context = (plan.generation_basis or {}).get("context", {})
    lifestyle = context.get("lifestyle_diet") or {}
    medical = context.get("medical") or {}
    preferences = context.get("preferences") or {}

    from app.services.ai.nutrition_generator import _parse_allergens

    preference_diet_type = preferences.get("diet_type")
    diet_type = PREFERENCE_DIET_TYPE_MAP.get(preference_diet_type, lifestyle.get("diet_type", "omnivore"))
    exclude_allergens = _parse_allergens(medical.get("allergies"), preferences.get("allergies"))
    disliked = set(preferences.get("disliked_foods") or [])
    already_in_day = {m["name"] for m in day["meals"]}

    pool = meals_for(
        pool_key_for_slot(meal_type), diet_type, exclude_allergens,
        cuisine_preference=preferences.get("cuisine_preference"), budget=preferences.get("budget"),
        cooking_time_preference=preferences.get("cooking_time_preference"),
        exclude_names=disliked | already_in_day,
    )
    return [m["name"] for m in pool]


def replace_meal_in_plan(
    db: Session, user: User, plan: NutritionPlan, day_index: int, meal_type: str, replacement_name: str | None
) -> NutritionPlan:
    """
    Sprint 4 objective 4: swaps a single meal in place, rescaled to the same
    calorie target the original meal held, preserving the day's overall
    structure. Also records the replacement in Nutrition Preferences
    (objective 5) so a repeated choice gets favored automatically.
    """
    if day_index < 0 or day_index >= len(plan.days):
        raise ValueError("day_index out of range")
    day = plan.days[day_index]
    meal_idx = next((i for i, m in enumerate(day["meals"]) if m["meal_type"] == meal_type), None)
    if meal_idx is None:
        raise ValueError("meal_type not found on this day")
    original = day["meals"][meal_idx]

    alternatives = get_meal_alternatives(db, user, plan, day_index, meal_type)
    if not alternatives:
        raise ValueError("No valid alternative meals are available for this slot")

    if replacement_name is None:
        import random
        replacement_name = random.choice(alternatives)
    elif replacement_name not in alternatives:
        raise ValueError("That meal isn't a valid alternative for this slot")

    replacement_meal = find_meal_by_name(replacement_name)
    if replacement_meal is None:
        raise ValueError("Unknown meal")

    scaled = _scale_meal(replacement_meal, original["calories"])
    scaled["meal_type"] = meal_type

    new_days = [dict(d) for d in plan.days]
    new_meals = list(new_days[day_index]["meals"])
    new_meals[meal_idx] = scaled
    new_days[day_index] = {**new_days[day_index], "meals": new_meals}
    plan.days = new_days
    db.commit()
    db.refresh(plan)

    nutrition_preferences_service.record_meal_replacement(db, user, original["name"], replacement_meal["name"])

    return plan
