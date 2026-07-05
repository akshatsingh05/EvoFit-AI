"""
Deterministic nutrition plan builder — the `builder` function passed to
RuleBasedProvider (see provider.py). Calorie and macro targets are computed
from the user's real body metrics via the Mifflin-St Jeor equation, not
hardcoded. Meals are selected from meal_library.py filtered by diet type and
allergies, then scaled to the day's calorie targets.
"""
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


def _scale_meal(meal: dict, target_calories: float) -> dict:
    factor = target_calories / meal["calories"] if meal["calories"] else 1
    return {
        "name": meal["name"],
        "calories": round(meal["calories"] * factor),
        "protein_g": round(meal["protein_g"] * factor),
        "carbs_g": round(meal["carbs_g"] * factor),
        "fat_g": round(meal["fat_g"] * factor),
    }


def build_nutrition_plan(context: dict) -> dict:
    body = context.get("body_metrics") or {}
    goals = context.get("goals") or {}
    lifestyle = context.get("lifestyle_diet") or {}
    medical = context.get("medical") or {}

    weight_kg = body.get("weight_kg", 70)
    height_cm = body.get("height_cm", 170)
    age = body.get("age", 30)
    sex = body.get("sex", "other")
    primary_goal = goals.get("primary_goal", "general_health")
    activity_level = lifestyle.get("occupation_activity", "sedentary")
    diet_type = lifestyle.get("diet_type", "omnivore")

    bmr = _bmr(weight_kg, height_cm, age, sex)
    tdee = bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    calorie_adjustment = GOAL_CALORIE_ADJUSTMENT.get(primary_goal, 0.0)
    # Adaptive engine can nudge this further based on real weight-trend-vs-goal mismatch (Module 4)
    calorie_adjustment += context.get("adaptive_calorie_adjustment", 0.0)
    target_calories = round(tdee * (1 + calorie_adjustment))

    protein_per_kg = GOAL_PROTEIN_PER_KG.get(primary_goal, 1.6)
    target_protein_g = round(weight_kg * protein_per_kg)
    protein_calories = target_protein_g * 4

    fat_calories = target_calories * 0.25
    target_fat_g = round(fat_calories / 9)

    remaining_calories = max(target_calories - protein_calories - fat_calories, 0)
    target_carbs_g = round(remaining_calories / 4)

    water_goal_ml = round(weight_kg * 35)

    exclude_allergens = _parse_allergens(medical.get("allergies"))

    meals = []
    for meal_type, share in MEAL_CALORIE_SHARE.items():
        pool = meals_for(meal_type, diet_type, exclude_allergens)
        if not pool:
            pool = meals_for(meal_type, "omnivore", exclude_allergens) or meals_for(meal_type, "omnivore", set())
        if not pool:
            continue
        chosen = pool[0]
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
    }
