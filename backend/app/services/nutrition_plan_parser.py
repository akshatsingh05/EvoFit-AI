"""
Feature 2 - parses raw nutrition-plan text into a structure comparable to
NutritionPlan.days: meals per day with calories/macros, plus plan-level
totals, water intake, and a rough cuisine guess. When a meal line doesn't
state macros explicitly, we estimate them from the closest match in the
meal library (flagged `is_estimated`) rather than leaving the plan
uncomparable.
"""
import re
from statistics import mean

from app.data.meal_library import MEALS

MEAL_TYPE_WORDS = {
    "breakfast": ["breakfast", "morning meal"],
    "lunch": ["lunch", "midday meal"],
    "dinner": ["dinner", "supper", "evening meal"],
    "snack": ["snack", "snacks"],
}
DAY_NAMES = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

CAL_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:kcal|cal|calories)\b", re.IGNORECASE)
PROTEIN_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g?\s*(?:protein)\b", re.IGNORECASE)
CARBS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g?\s*(?:carb[s]?|carbohydrates?)\b", re.IGNORECASE)
FAT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*g?\s*fat\b", re.IGNORECASE)
WATER_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(ml|l|liters?|litres?|oz|cups?)\s*(?:of\s*)?water", re.IGNORECASE)
WATER_RE_REVERSED = re.compile(r"water\D{0,12}?(\d+(?:\.\d+)?)\s*(ml|l|liters?|litres?|oz|cups?)\b", re.IGNORECASE)

CUISINE_KEYWORDS = {
    "mediterranean": ["olive oil", "hummus", "feta", "falafel", "quinoa", "tzatziki"],
    "asian": ["rice", "soy", "tofu", "stir-fry", "stir fry", "noodle", "sushi", "teriyaki", "curry"],
    "mexican": ["taco", "burrito", "salsa", "beans", "tortilla", "guacamole"],
    "american": ["burger", "steak", "sandwich", "fries", "bbq", "chicken breast"],
    "indian": ["curry", "paneer", "naan", "dal", "masala", "chapati"],
}

_ALL_MEALS_FLAT = [(mtype, m) for mtype, meals in MEALS.items() for m in meals]


def _clean_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"^[\-\*\u2022•]+\s*", "", line)
    line = re.sub(r"^\d+[\.\)]\s*", "", line)
    line = line.replace("|", " ").strip()
    return line


def _is_day_header(line: str) -> tuple[bool, str | None]:
    lowered = line.lower().strip().rstrip(":")
    for day in DAY_NAMES:
        if lowered == day or lowered.startswith(day + " ") or lowered.startswith(day + ","):
            return True, line.strip().rstrip(":")
    if re.match(r"^day\s*\d+\b", lowered):
        return True, line.strip().rstrip(":")
    return False, None


def _detect_meal_type(line: str) -> str | None:
    lowered = line.lower().strip().rstrip(":")
    for meal_type, words in MEAL_TYPE_WORDS.items():
        for w in words:
            if lowered == w or lowered.startswith(w + ":") or lowered.startswith(w + " -") or lowered.startswith(w):
                if len(lowered.split()) <= 3:
                    return meal_type
    return None


def _match_library_meal(name: str) -> tuple[str, dict] | None:
    lowered = name.lower().strip()
    best = None
    best_score = 0
    for mtype, meal in _ALL_MEALS_FLAT:
        meal_lower = meal["name"].lower()
        if meal_lower == lowered:
            return mtype, meal
        # token overlap score
        tokens_a = set(lowered.split())
        tokens_b = set(meal_lower.split())
        overlap = len(tokens_a & tokens_b)
        if overlap > best_score:
            best_score = overlap
            best = (mtype, meal)
    if best and best_score >= 1:
        return best
    return None


def _guess_cuisine(text: str) -> str:
    lowered = text.lower()
    scores = {c: sum(lowered.count(kw) for kw in kws) for c, kws in CUISINE_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "unspecified"


def parse_nutrition_text(raw_text: str) -> dict:
    lines = [_clean_line(l) for l in raw_text.splitlines()]
    lines = [l for l in lines if l != ""]

    days: list[dict] = []
    current_day = None
    current_meal_type = "snack"
    unassigned_meals: list[dict] = []
    water_ml_found: list[float] = []

    def _new_day(name):
        return {"day_name": name, "meals": [], "total_calories": 0, "total_protein_g": 0,
                 "total_carbs_g": 0, "total_fat_g": 0}

    for line in lines:
        is_header, label = _is_day_header(line)
        if is_header:
            current_day = _new_day(label)
            days.append(current_day)
            current_meal_type = "breakfast"
            continue

        water_match = WATER_RE.search(line) or WATER_RE_REVERSED.search(line)
        if water_match:
            amount, unit = float(water_match.group(1)), water_match.group(2).lower()
            ml = amount
            if unit in ("l", "liter", "liters", "litre", "litres"):
                ml = amount * 1000
            elif unit == "oz":
                ml = amount * 29.5735
            elif unit.startswith("cup"):
                ml = amount * 240
            water_ml_found.append(ml)
            continue

        detected_meal_type = _detect_meal_type(line)
        if detected_meal_type:
            current_meal_type = detected_meal_type
            continue

        # Otherwise, it's a food/meal line.
        calories_match = CAL_RE.search(line)
        protein_match = PROTEIN_RE.search(line)
        carbs_match = CARBS_RE.search(line)
        fat_match = FAT_RE.search(line)

        name = line
        for m in (calories_match, protein_match, carbs_match, fat_match):
            if m:
                name = name.replace(m.group(0), "")
        name = re.sub(r"[\-,:]+\s*$", "", name).strip(" -:,")
        if not name:
            continue

        is_estimated = not (calories_match and protein_match)
        if calories_match:
            calories = float(calories_match.group(1))
        else:
            calories = None
        protein_g = float(protein_match.group(1)) if protein_match else None
        carbs_g = float(carbs_match.group(1)) if carbs_match else None
        fat_g = float(fat_match.group(1)) if fat_match else None

        library_match = None
        if calories is None or protein_g is None:
            library_match = _match_library_meal(name)
            if library_match:
                _, meal_data = library_match
                calories = calories if calories is not None else meal_data["calories"]
                protein_g = protein_g if protein_g is not None else meal_data["protein_g"]
                carbs_g = carbs_g if carbs_g is not None else meal_data["carbs_g"]
                fat_g = fat_g if fat_g is not None else meal_data["fat_g"]

        # Final fallback so every meal is always comparable, even totally unknown foods.
        calories = calories if calories is not None else 400
        protein_g = protein_g if protein_g is not None else 20
        carbs_g = carbs_g if carbs_g is not None else 40
        fat_g = fat_g if fat_g is not None else 12

        meal_entry = {
            "meal_type": current_meal_type,
            "name": name,
            "calories": round(calories),
            "protein_g": round(protein_g),
            "carbs_g": round(carbs_g),
            "fat_g": round(fat_g),
            "is_estimated": is_estimated,
            "raw_line": line,
        }

        if current_day is None:
            unassigned_meals.append(meal_entry)
        else:
            current_day["meals"].append(meal_entry)

    if unassigned_meals and not days:
        days.append({**_new_day("Day 1"), "meals": unassigned_meals})
    elif unassigned_meals:
        days.insert(0, {**_new_day("Day 1"), "meals": unassigned_meals})

    for day in days:
        day["total_calories"] = sum(m["calories"] for m in day["meals"])
        day["total_protein_g"] = sum(m["protein_g"] for m in day["meals"])
        day["total_carbs_g"] = sum(m["carbs_g"] for m in day["meals"])
        day["total_fat_g"] = sum(m["fat_g"] for m in day["meals"])

    all_meals = [m for d in days for m in d["meals"]]
    avg_daily_calories = round(mean([d["total_calories"] for d in days])) if days else 0
    avg_daily_protein = round(mean([d["total_protein_g"] for d in days])) if days else 0
    avg_daily_carbs = round(mean([d["total_carbs_g"] for d in days])) if days else 0
    avg_daily_fat = round(mean([d["total_fat_g"] for d in days])) if days else 0
    avg_water_ml = round(mean(water_ml_found)) if water_ml_found else None

    return {
        "days": days,
        "total_meals": len(all_meals),
        "unique_foods": len({m["name"].lower() for m in all_meals}),
        "estimated_meal_count": sum(1 for m in all_meals if m["is_estimated"]),
        "avg_daily_calories": avg_daily_calories,
        "avg_daily_protein_g": avg_daily_protein,
        "avg_daily_carbs_g": avg_daily_carbs,
        "avg_daily_fat_g": avg_daily_fat,
        "avg_water_ml": avg_water_ml,
        "cuisine_guess": _guess_cuisine(raw_text),
    }
