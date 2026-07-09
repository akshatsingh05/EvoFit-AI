"""
Feature 3 - compares an ImportedPlan against the user's current EvoFit AI
plan. Produces the structured metrics the frontend renders as cards/tables/
progress bars/badges, plus the raw numbers Feature 4 (AI analysis) and
Feature 5 (suggestions) reason over.
"""
import statistics

from app.models.user import User
from app.models.workout import WorkoutPlan
from app.models.nutrition import NutritionPlan
from app.services.workout_plan_parser import _infer_muscle_group, _match_library_exercise

MUSCLE_GROUPS = ["chest", "back", "legs", "shoulders", "arms", "core", "cardio"]


def _evofit_workout_metrics(plan: WorkoutPlan) -> dict:
    muscle_volume = {g: 0 for g in MUSCLE_GROUPS}
    total_exercises = 0
    workout_days = 0
    equipment_tiers_seen = set()

    for day in plan.schedule:
        if day.get("is_rest_day"):
            continue
        exercises = day.get("exercises", [])
        if not exercises:
            continue
        workout_days += 1
        for ex in exercises:
            total_exercises += 1
            library_match = _match_library_exercise(ex["name"])
            group = _infer_muscle_group(ex["name"], library_match["focus"] if library_match else None)
            if group in muscle_volume:
                muscle_volume[group] += ex.get("sets", 1) or 1
            if library_match:
                equipment_tiers_seen.add(library_match.get("equipment", "unspecified"))

    equipment_guess = "full_gym" if "full_gym" in equipment_tiers_seen else (
        "home_basic" if "home_basic" in equipment_tiers_seen else "none"
    )

    return {
        "workout_days_count": workout_days,
        "rest_days_count": sum(1 for d in plan.schedule if d.get("is_rest_day")),
        "total_exercises": total_exercises,
        "muscle_volume": muscle_volume,
        "equipment_guess": equipment_guess,
    }


def _recovery_score(schedule_like_days: list[dict]) -> dict:
    """Longest streak of consecutive training days without a rest day -- a
    rough recovery proxy. Lower is generally better recovery spacing."""
    longest_streak = 0
    current_streak = 0
    for day in schedule_like_days:
        is_training = not day.get("is_rest_day") and day.get("exercises")
        if is_training:
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
        else:
            current_streak = 0
    return {"longest_consecutive_training_days": longest_streak}


def _muscle_balance_score(muscle_volume: dict) -> float:
    """0-100, 100 = perfectly even volume distribution across trained groups."""
    trained = {g: v for g, v in muscle_volume.items() if g != "cardio" and v > 0}
    if len(trained) < 2:
        return 50.0
    values = list(trained.values())
    avg = statistics.mean(values)
    if avg == 0:
        return 50.0
    stdev = statistics.pstdev(values)
    cv = stdev / avg  # coefficient of variation
    return round(max(0.0, 100 - (cv * 100)), 1)


def _workout_effectiveness(metrics: dict) -> int:
    score = 0
    # Frequency: 3-6 training days/week is the well-supported sweet spot.
    freq = metrics["workout_days_count"]
    score += 35 if 3 <= freq <= 6 else (20 if freq in (2, 7) else 10)
    # Volume: total exercise count as a rough proxy for weekly volume.
    total = metrics["total_exercises"]
    score += 30 if 12 <= total <= 30 else (18 if total > 0 else 0)
    # Balance across muscle groups.
    score += round(metrics["muscle_balance_score"] * 0.35)
    return min(100, score)


def compare_workout_plans(imported_parsed: dict, evofit_plan: WorkoutPlan | None) -> dict:
    mine = {
        "workout_days_count": imported_parsed["workout_days_count"],
        "rest_days_count": imported_parsed["rest_days_count"],
        "total_exercises": imported_parsed["total_exercises"],
        "muscle_volume": {g: imported_parsed["muscle_volume"].get(g, 0) for g in MUSCLE_GROUPS},
        "equipment_guess": imported_parsed["equipment_guess"],
        "detected_split": imported_parsed["detected_split"],
        "training_style_guess": imported_parsed["training_style_guess"],
        "recovery": _recovery_score(imported_parsed["days"]),
    }
    mine["muscle_balance_score"] = _muscle_balance_score(mine["muscle_volume"])
    mine["effectiveness_score"] = _workout_effectiveness(mine)

    if evofit_plan is None:
        evofit = None
    else:
        evofit = _evofit_workout_metrics(evofit_plan)
        evofit["recovery"] = _recovery_score(evofit_plan.schedule)
        evofit["muscle_balance_score"] = _muscle_balance_score(evofit["muscle_volume"])
        evofit["effectiveness_score"] = _workout_effectiveness(evofit)

    return {
        "type": "workout",
        "mine": mine,
        "evofit": evofit,
        "muscle_groups": MUSCLE_GROUPS,
    }


def _nutrition_metrics_from_days(days: list[dict], key_map: dict) -> dict:
    """key_map lets this work for both the imported-plan shape and the
    EvoFit NutritionPlan.days shape, which use different field names."""
    if not days:
        return {
            "avg_daily_calories": 0, "avg_daily_protein_g": 0, "avg_daily_carbs_g": 0,
            "avg_daily_fat_g": 0, "avg_water_ml": None, "unique_foods": 0, "meal_types_covered": [],
        }
    cal = [d[key_map["calories"]] for d in days]
    pro = [d[key_map["protein"]] for d in days]
    carb = [d[key_map["carbs"]] for d in days]
    fat = [d[key_map["fat"]] for d in days]
    water_vals = [d[key_map["water"]] for d in days if key_map.get("water") and d.get(key_map["water"])]
    meal_names = set()
    meal_types = set()
    for d in days:
        for m in d.get("meals", []):
            meal_names.add(m.get("name", "").lower())
            meal_types.add(m.get("meal_type", ""))

    return {
        "avg_daily_calories": round(statistics.mean(cal)) if cal else 0,
        "avg_daily_protein_g": round(statistics.mean(pro)) if pro else 0,
        "avg_daily_carbs_g": round(statistics.mean(carb)) if carb else 0,
        "avg_daily_fat_g": round(statistics.mean(fat)) if fat else 0,
        "avg_water_ml": round(statistics.mean(water_vals)) if water_vals else None,
        "unique_foods": len(meal_names),
        "meal_types_covered": sorted(meal_types),
    }


def _nutrition_effectiveness(metrics: dict, target_calories: int | None, target_protein: int | None) -> int:
    score = 0
    if target_calories:
        diff_pct = abs(metrics["avg_daily_calories"] - target_calories) / target_calories
        score += 35 if diff_pct <= 0.1 else (20 if diff_pct <= 0.25 else 8)
    else:
        score += 20
    if target_protein:
        diff_pct = abs(metrics["avg_daily_protein_g"] - target_protein) / max(target_protein, 1)
        score += 30 if diff_pct <= 0.1 else (18 if diff_pct <= 0.25 else 8)
    else:
        score += 15
    score += min(20, len(metrics["meal_types_covered"]) * 5)
    score += 15 if (metrics["avg_water_ml"] or 0) >= 2000 else 5
    return min(100, score)


def compare_nutrition_plans(imported_parsed: dict, evofit_plan: NutritionPlan | None) -> dict:
    mine = _nutrition_metrics_from_days(
        imported_parsed["days"],
        {"calories": "total_calories", "protein": "total_protein_g", "carbs": "total_carbs_g",
         "fat": "total_fat_g", "water": None},
    )
    mine["avg_water_ml"] = imported_parsed.get("avg_water_ml")
    mine["cuisine_guess"] = imported_parsed.get("cuisine_guess")

    evofit = None
    target_calories = target_protein = None
    if evofit_plan is not None:
        evofit_days = evofit_plan.days
        evofit = _nutrition_metrics_from_days(
            evofit_days,
            {"calories": "target_calories", "protein": "target_protein_g", "carbs": "target_carbs_g",
             "fat": "target_fat_g", "water": "water_goal_ml"},
        )
        target_calories = evofit["avg_daily_calories"]
        target_protein = evofit["avg_daily_protein_g"]
        evofit["effectiveness_score"] = _nutrition_effectiveness(evofit, target_calories, target_protein)

    mine["effectiveness_score"] = _nutrition_effectiveness(mine, target_calories, target_protein)

    return {
        "type": "nutrition",
        "mine": mine,
        "evofit": evofit,
    }
