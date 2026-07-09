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

Sprint 4 (Personalization Engine) changes — all optional, falling back to
Sprint 1-3 behavior until the user sets a Nutrition Preference:
- `diet_type` from Nutrition Preferences (vegetarian/vegan/eggetarian/
  non_vegetarian) overrides the onboarding diet_type when set.
- `cuisine_preference`, `budget`, `cooking_time_preference` are soft sort
  preferences applied via meal_library.meals_for.
- `favorite_foods` / `preferred_snacks` are boosted to the front of
  selection; `disliked_foods` and preference `allergies` are hard-excluded
  in addition to medical allergies.
- `meals_per_day` (3-6) changes the day's meal structure via
  MEAL_STRUCTURE_BY_COUNT instead of always generating the fixed 4-meal day.
- `water_goal_ml`, when set, overrides the weight-derived default.
- `meal_replacement_memory` (Sprint 4 objective 5): a meal replaced with the
  same alternative 2+ times is substituted automatically going forward.
"""
import random

from app.data.meal_library import (
    meals_for,
    MEAL_STRUCTURE_BY_COUNT,
    MEAL_CALORIE_SHARE,
    pool_key_for_slot,
    find_meal_by_name,
    PREFERENCE_DIET_TYPE_MAP,
)

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


def _parse_allergens(allergy_text: str | None, preference_allergies: list | None = None) -> set:
    allergens = set()
    if allergy_text:
        text = allergy_text.lower()
        allergens |= {a for a in COMMON_ALLERGENS if a in text}
    for entry in preference_allergies or []:
        low = entry.lower()
        allergens |= {a for a in COMMON_ALLERGENS if a in low}
    return allergens


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


def _pick_meal(pool: list, rng: random.Random, avoid_names: set, boosted_names: set) -> dict | None:
    if not pool:
        return None
    shuffled = pool[:]
    rng.shuffle(shuffled)
    if boosted_names:
        shuffled.sort(key=lambda m: 0 if m["name"] in boosted_names else 1)
    fresh = [m for m in shuffled if m["name"] not in avoid_names]
    return (fresh or shuffled)[0]


def _apply_replacement_memory(meal: dict, meal_slot: str, dominant_map: dict, diet_type: str, exclude_allergens: set) -> dict:
    """Sprint 4 objective 5: substitutes a repeatedly-chosen replacement, if it's
    still valid for the current diet type and allergen exclusions."""
    if not dominant_map or meal is None:
        return meal
    replacement_name = dominant_map.get(meal["name"])
    if not replacement_name:
        return meal
    replacement = find_meal_by_name(replacement_name)
    if replacement is None:
        return meal
    is_compatible = diet_type in replacement["diet_types"] and not (set(replacement["allergens"]) & exclude_allergens)
    return replacement if is_compatible else meal


def build_nutrition_plan(context: dict) -> dict:
    body = context.get("body_metrics") or {}
    goals = context.get("goals") or {}
    lifestyle = context.get("lifestyle_diet") or {}
    medical = context.get("medical") or {}
    preferences = context.get("preferences") or {}
    variation_seed = context.get("variation_seed", "default")
    avoid_meal_names = set(context.get("avoid_meal_names") or [])

    weight_kg = body.get("weight_kg", 70)
    height_cm = body.get("height_cm", 170)
    age = body.get("age", 30)
    sex = body.get("sex", "other")
    primary_goal = goals.get("primary_goal", "general_health")
    activity_level = lifestyle.get("occupation_activity", "sedentary")

    # Sprint 4: a Nutrition Preferences diet_type, when set, overrides the
    # onboarding diet_type — see PREFERENCE_DIET_TYPE_MAP for how the
    # preference vocabulary (vegetarian/vegan/eggetarian/non_vegetarian) maps
    # onto this library's tags (omnivore/vegetarian/vegan/pescatarian/keto).
    preference_diet_type = preferences.get("diet_type")
    diet_type = PREFERENCE_DIET_TYPE_MAP.get(preference_diet_type, lifestyle.get("diet_type", "omnivore"))

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

    # Sprint 4: an explicit Nutrition Preferences water goal overrides the
    # weight-derived default when the user has set one.
    water_goal_ml = preferences.get("water_goal_ml") or round(weight_kg * 35)

    exclude_allergens = _parse_allergens(medical.get("allergies"), preferences.get("allergies"))
    prefer_low_glycemic = bool(conditions & GLUCOSE_SENSITIVE_CONDITIONS)

    cuisine_preference = preferences.get("cuisine_preference")
    budget = preferences.get("budget")
    cooking_time_preference = preferences.get("cooking_time_preference")
    disliked_foods = set(preferences.get("disliked_foods") or [])
    boosted_names = set(preferences.get("favorite_foods") or []) | set(preferences.get("preferred_snacks") or [])
    dominant_replacements = preferences.get("dominant_replacements") or {}

    meals_per_day = preferences.get("meals_per_day") or lifestyle.get("meals_per_day") or 4
    meal_structure = MEAL_STRUCTURE_BY_COUNT.get(meals_per_day, list(MEAL_CALORIE_SHARE.items()))

    rng = random.Random(f"{variation_seed}:nutrition")

    meals = []
    for meal_slot, share in meal_structure:
        pool_key = pool_key_for_slot(meal_slot)
        pool = meals_for(
            pool_key, diet_type, exclude_allergens, prefer_low_glycemic,
            cuisine_preference=cuisine_preference, budget=budget,
            cooking_time_preference=cooking_time_preference, exclude_names=disliked_foods,
        )
        if not pool:
            pool = meals_for(pool_key, "omnivore", exclude_allergens, prefer_low_glycemic, exclude_names=disliked_foods) or meals_for(
                pool_key, "omnivore", set(), prefer_low_glycemic, exclude_names=disliked_foods
            )
        chosen = _pick_meal(pool, rng, avoid_meal_names, boosted_names)
        chosen = _apply_replacement_memory(chosen, meal_slot, dominant_replacements, diet_type, exclude_allergens)
        if chosen is None:
            continue
        meal_target_calories = target_calories * share
        scaled = _scale_meal(chosen, meal_target_calories)
        scaled["meal_type"] = meal_slot
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
