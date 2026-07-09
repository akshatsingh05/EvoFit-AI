"""
Feature 4 (AI analysis / observations) and Feature 5 (actionable
suggestions), both rule-based per the project spec (no LLM integration).
Every observation and suggestion is derived from the actual comparison
numbers for this user's imported plan -- never a generic templated line
with no data behind it.
"""
import random

from app.data.exercise_library import EXERCISES

JUNK_FOOD_KEYWORDS = ["fries", "soda", "pizza", "burger", "candy", "chips", "donut", "cake", "cookie",
                       "fried chicken", "milkshake", "energy drink"]

LOW_VOLUME_THRESHOLD_SETS = 6  # per muscle group per week, below this is "low"
TARGET_TRAINING_DAYS_MIN = 3
TARGET_TRAINING_DAYS_MAX = 6


def _pick_replacement_exercise(muscle_group_keyword: str, exclude_name: str, equipment: str) -> str | None:
    focus_map = {"chest": "push", "back": "pull", "legs": "lower_body", "shoulders": "push",
                 "arms": "pull", "core": "full_body", "cardio": "cardio"}
    focus = focus_map.get(muscle_group_keyword)
    if not focus:
        return None
    pool = [ex for ex in EXERCISES if ex["focus"] == focus and ex["name"].lower() != exclude_name.lower()]
    if equipment in ("home_basic", "full_gym"):
        pool = [ex for ex in pool if ex["equipment"] in ("none", "home_basic", "full_gym")] or pool
    if not pool:
        return None
    return random.choice(pool)["name"]


def analyze_workout(comparison: dict, imported_parsed: dict) -> tuple[list[str], list[dict]]:
    observations: list[str] = []
    suggestions: list[dict] = []

    mine = comparison["mine"]
    evofit = comparison.get("evofit")

    # --- Frequency ---
    freq = mine["workout_days_count"]
    if freq < TARGET_TRAINING_DAYS_MIN:
        observations.append(
            f"Your plan only trains {freq} day(s) a week, which is below the "
            f"{TARGET_TRAINING_DAYS_MIN}-{TARGET_TRAINING_DAYS_MAX} day range generally recommended for steady progress."
        )
        suggestions.append({
            "type": "frequency",
            "title": "Add another training day",
            "detail": f"Increase from {freq} to at least {TARGET_TRAINING_DAYS_MIN} training days per week.",
            "reason": f"Only {freq} training day(s) were detected in your imported plan.",
        })
    elif freq > TARGET_TRAINING_DAYS_MAX:
        observations.append(
            f"Your plan trains {freq} days a week with a longest streak of "
            f"{mine['recovery']['longest_consecutive_training_days']} consecutive days -- recovery may be limited."
        )

    # --- Recovery ---
    streak = mine["recovery"]["longest_consecutive_training_days"]
    if streak >= 4:
        observations.append(
            f"You have {streak} consecutive training days with no rest day in between, "
            "which can limit recovery between sessions."
        )
        suggestions.append({
            "type": "recovery",
            "title": "Insert a rest day",
            "detail": f"Break up the {streak}-day training streak with at least one rest or active-recovery day.",
            "reason": f"{streak} consecutive training days were detected with no rest day.",
        })

    # --- Muscle volume / balance ---
    for group, sets in mine["muscle_volume"].items():
        if group == "cardio":
            continue
        if sets == 0 and mine["workout_days_count"] > 0:
            observations.append(f"No {group} training volume was detected anywhere in your plan.")
            replacement = _pick_replacement_exercise(group, "", mine["equipment_guess"])
            if replacement:
                suggestions.append({
                    "type": "volume",
                    "title": f"Add {group} training",
                    "detail": f"Add {replacement} to build {group} volume.",
                    "reason": f"{group.title()} volume is currently 0 sets/week in your imported plan.",
                })
        elif 0 < sets < LOW_VOLUME_THRESHOLD_SETS:
            observations.append(
                f"{group.title()} volume is low at {sets} sets/week (a common minimum-effective target is "
                f"around {LOW_VOLUME_THRESHOLD_SETS}-10 sets/week per muscle group)."
            )
            weakest_exercise = next(
                (ex["name"] for d in imported_parsed["days"] for ex in d["exercises"] if ex["muscle_group"] == group),
                None,
            )
            replacement = _pick_replacement_exercise(group, weakest_exercise or "", mine["equipment_guess"])
            if replacement and weakest_exercise:
                suggestions.append({
                    "type": "volume",
                    "title": f"Increase {group} volume",
                    "detail": f"Replace {weakest_exercise} with {replacement} to add {group} volume, or add an extra set.",
                    "reason": f"{group.title()} volume is low ({sets} sets/week).",
                })

    if evofit:
        for group in mine["muscle_volume"]:
            mine_v, evo_v = mine["muscle_volume"][group], evofit["muscle_volume"].get(group, 0)
            if evo_v > 0 and mine_v < evo_v * 0.5 and group != "cardio":
                observations.append(
                    f"EvoFit AI targets roughly {evo_v} sets/week of {group} training for your profile, "
                    f"well above the {mine_v} sets/week in your imported plan."
                )

    # --- Muscle balance ---
    if mine["muscle_balance_score"] < 50:
        observations.append(
            "Training volume is unevenly distributed across muscle groups, which can lead to imbalances over time."
        )
        suggestions.append({
            "type": "balance",
            "title": "Even out muscle group volume",
            "detail": "Redistribute sets so no single muscle group has dramatically more volume than the others.",
            "reason": f"Muscle balance score is {mine['muscle_balance_score']}/100.",
        })

    # --- Unmatched / unclear exercises ---
    if imported_parsed.get("unmatched_exercise_count", 0) > 0:
        observations.append(
            f"{imported_parsed['unmatched_exercise_count']} exercise(s) in your plan weren't recognized in the "
            "exercise library; they were kept as-is and still counted toward volume."
        )

    if not observations:
        observations.append("Your workout plan looks well-structured across frequency, recovery, and volume.")

    return observations, suggestions


def analyze_nutrition(comparison: dict, imported_parsed: dict) -> tuple[list[str], list[dict]]:
    observations: list[str] = []
    suggestions: list[dict] = []

    mine = comparison["mine"]
    evofit = comparison.get("evofit")

    if evofit:
        protein_gap = evofit["avg_daily_protein_g"] - mine["avg_daily_protein_g"]
        if protein_gap > 10:
            observations.append(
                f"Protein intake averages {mine['avg_daily_protein_g']}g/day, "
                f"{round(protein_gap)}g below your EvoFit AI target of {evofit['avg_daily_protein_g']}g/day."
            )
            suggestions.append({
                "type": "protein",
                "title": f"Increase protein by {round(protein_gap)}g",
                "detail": f"Add roughly {round(protein_gap)}g of protein per day (e.g. a protein shake or extra "
                           "lean meat/tofu serving) to close the gap.",
                "reason": f"Protein is {round(protein_gap)}g/day below your EvoFit AI target.",
            })

        cal_gap = mine["avg_daily_calories"] - evofit["avg_daily_calories"]
        if abs(cal_gap) > evofit["avg_daily_calories"] * 0.15 and evofit["avg_daily_calories"] > 0:
            direction = "above" if cal_gap > 0 else "below"
            observations.append(
                f"Average daily calories ({mine['avg_daily_calories']} kcal) are "
                f"{abs(round(cal_gap))} kcal {direction} your EvoFit AI target of {evofit['avg_daily_calories']} kcal."
            )
    else:
        if mine["avg_daily_protein_g"] < 90:
            observations.append(f"Protein intake averages {mine['avg_daily_protein_g']}g/day, which is on the low side.")
            suggestions.append({
                "type": "protein",
                "title": "Increase protein by 25g",
                "detail": "Add roughly 25g of protein per day (e.g. a protein shake or extra lean meat/tofu serving).",
                "reason": f"Protein intake averages only {mine['avg_daily_protein_g']}g/day.",
            })

    # --- Water ---
    water = mine.get("avg_water_ml")
    if water is None:
        observations.append("Water intake wasn't specified anywhere in your imported plan.")
    elif water < 2000:
        deficit = 2000 - water
        observations.append(f"Water intake averages {water}ml/day, below the commonly recommended ~2000ml/day.")
        suggestions.append({
            "type": "hydration",
            "title": f"Increase water intake by {round(deficit)}ml",
            "detail": f"Add roughly {round(deficit)}ml (about {round(deficit/250)} glasses) of water per day.",
            "reason": f"Water intake averages {water}ml/day, below the ~2000ml/day target.",
        })

    # --- Carb timing around training ---
    if mine["avg_daily_carbs_g"] < 130 and mine["avg_daily_calories"] > 0:
        observations.append(
            f"Carbohydrate intake averages {mine['avg_daily_carbs_g']}g/day, which may be insufficient "
            "to fuel workouts, especially on training days."
        )
        suggestions.append({
            "type": "carbs",
            "title": "Add pre-workout carbohydrates",
            "detail": "Add a carb-focused snack (fruit, oats, rice) 1-2 hours before training sessions.",
            "reason": f"Average carbohydrate intake is {mine['avg_daily_carbs_g']}g/day.",
        })

    # --- Food variety ---
    if mine["unique_foods"] < 8:
        observations.append(f"Only {mine['unique_foods']} unique foods were detected across your plan, limiting variety.")
        suggestions.append({
            "type": "variety",
            "title": "Increase food variety",
            "detail": "Rotate in 3-5 additional meal options to broaden micronutrient intake and reduce diet fatigue.",
            "reason": f"Only {mine['unique_foods']} unique foods were detected.",
        })

    # --- Junk food frequency ---
    junk_hits = 0
    for day in imported_parsed["days"]:
        for meal in day["meals"]:
            if any(kw in meal["name"].lower() for kw in JUNK_FOOD_KEYWORDS):
                junk_hits += 1
    if junk_hits > 0:
        observations.append(f"{junk_hits} meal(s) in your plan matched common lower-nutrient/'junk food' items.")
        suggestions.append({
            "type": "food_quality",
            "title": "Reduce junk food frequency",
            "detail": f"Swap {min(junk_hits, 2)} of the {junk_hits} identified item(s) for a whole-food alternative.",
            "reason": f"{junk_hits} meal(s) matched common lower-nutrient food keywords.",
        })

    # --- Meal timing coverage ---
    covered = set(mine.get("meal_types_covered", []))
    missing = {"breakfast", "lunch", "dinner"} - covered
    if missing:
        observations.append(f"No {', '.join(sorted(missing))} entries were found in the imported plan.")

    if not observations:
        observations.append("Your nutrition plan looks well-balanced across calories, macros, and hydration.")

    return observations, suggestions
