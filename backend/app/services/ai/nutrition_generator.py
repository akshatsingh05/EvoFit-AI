"""
Deterministic nutrition plan builder — the `builder` function passed to
RuleBasedProvider (see provider.py). Calorie and macro targets are computed
from the user's real body metrics via the Mifflin-St Jeor equation, not
hardcoded. Meals are selected from meal_library.py filtered by diet type and
allergies, then scaled to the day's calorie targets.

Sprint 1 fix: meal selection previously always took the first match in the
filtered pool, so every user with the same diet type got identical meals.
Selection is now seeded per-user/per-regeneration (same pattern as the
workout generator) and avoids repeating the immediately previous plan's
meals when alternatives exist.
"""
import random

from app.data.meal_library import meals_for, MEAL_CALORIE_SHARE

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "active": 1.55,
    "very_active": 1.725,
}

GOAL_CALORIE_ADJUSTMENT = {
    "lose_weight": -0.20,
    "build_muscle": 0.10,
    "improve_endurance": 0.0,
    "general_health": 0.0,
    "sport_specific": 0.05,
}

GOAL_PROTEIN_PER_KG = {
    "lose_weight": 2.2,
    "build_muscle": 2.0,
    "improve_endurance": 1.6,
    "general_health": 1.6,
    "sport_specific": 1.8,
}

COMMON_ALLERGENS = ["nuts", "dairy", "gluten", "shellfish", "fish", "eggs", "soy"]
GLUCOSE_SENSITIVE_CONDITIONS = {"diabetes_type_1", "diabetes_type_2"}


def _parse_allergens(allergy_text: str | None) -> set[str]:
    if not allergy_text:
        return set()
    text = allergy_text.lower()
    return {a for a in COMMON_ALLERGENS if a in text}


def _bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    # Mifflin-St Jeor equation
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if sex == "male":
        return base + 5
    if sex == "female":
        return base - 161
    return base - 78  # midpoint offset for "other"


def _calculate_bmi(weight_kg: float, height_cm: float) -> float | None:
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def _scale_meal(meal: dict, target_calories: float) -> dict:
    factor = target_calories / meal["calories"] if meal["calories"] else 1
    return {
        "name": meal["name"],
        "calories": round(meal["calories"] * factor),
        "protein_g": round(meal["protein_g"] * factor),
        "carbs_g": round(meal["carbs_g"] * factor),
        "fat_g": round(meal["fat_g"] * factor),
    }


def _pick_meal(pool: list, rng: random.Random, avoid_names: set) -> dict | None:
    if not pool:
        return None
    shuffled = pool[:]
    rng.shuffle(shuffled)
    fresh = [m for m in shuffled if m["name"] not in avoid_names]
    return (fresh or shuffled)[0]


def build_nutrition_plan(context: dict) -> dict:
    body = context.get("body_metrics") or {}
    goals = context.get("goals") or {}
    lifestyle = context.get("lifestyle_diet") or {}
    medical = context.get("medical") or {}
    variation_seed = context.get("variation_seed", "default")
    avoid_meal_names = set(context.get("avoid_meal_names") or [])

    weight_kg = body.get("weight_kg", 70)
    height_cm = body.get("height_cm", 170)
    age = body.get("age", 30)
    sex = body.get("sex", "other")
    primary_goal = goals.get("primary_goal", "general_health")
    activity_level = lifestyle.get("occupation_activity", "sedentary")
    diet_type = lifestyle.get("diet_type", "omnivore")
    conditions = set(medical.get("conditions") or [])

    bmi = _calculate_bmi(weight_kg, height_cm)

    bmr = _bmr(weight_kg, height_cm, age, sex)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    calorie_adjustment = GOAL_CALORIE_ADJUSTMENT.get(primary_goal, 0.0)
    # Adaptive engine can nudge this further based on real weight-trend-vs-goal mismatch (Module 4)
    calorie_adjustment += context.get("adaptive_calorie_adjustment", 0.0)
    target_calories = round(tdee * (1 + calorie_adjustment))

    protein_per_kg = GOAL_PROTEIN_PER_KG.get(primary_goal, 1.6)
    target_protein_g = round(weight_kg * protein_per_kg)
    protein_calories = target_protein_g * 4

    # Glucose-sensitive conditions shift the macro split toward more fat/protein,
    # less carbohydrate, on top of whatever the goal already sets.
    fat_share = 0.30 if conditions & GLUCOSE_SENSITIVE_CONDITIONS else 0.25
    fat_calories = target_calories * fat_share
    target_fat_g = round(fat_calories / 9)

    remaining_calories = max(target_calories - protein_calories - fat_calories, 0)
    target_carbs_g = round(remaining_calories / 4)

    water_goal_ml = round(weight_kg * 35)

    exclude_allergens = _parse_allergens(medical.get("allergies"))
    prefer_low_glycemic = bool(conditions & GLUCOSE_SENSITIVE_CONDITIONS)

    rng = random.Random(f"{variation_seed}:nutrition")

    meals = []
    for meal_type, share in MEAL_CALORIE_SHARE.items():
        pool = meals_for(meal_type, diet_type, exclude_allergens, prefer_low_glycemic)
        if not pool:
            pool = meals_for(meal_type, "omnivore", exclude_allergens, prefer_low_glycemic) or meals_for(
                meal_type, "omnivore", set(), prefer_low_glycemic
            )
        chosen = _pick_meal(pool, rng, avoid_meal_names)
        if chosen is None:
            continue
        meal_target_calories = target_calories * share
        scaled = _scale_meal(chosen, meal_target_calories)
        scaled["meal_type"] = meal_type
        meals.append(scaled)

    return {
        "target_calories": target_calories,
        "target_protein_g": target_protein_g,
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
        "water_goal_ml": water_goal_ml,
        "meals": meals,
        "bmi": bmi,
    }
