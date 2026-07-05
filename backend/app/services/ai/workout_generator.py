"""
Deterministic workout plan builder. This is the `builder` function passed to
RuleBasedProvider — see provider.py for why this is structured this way.
Everything here is derived from the user's actual profile; nothing is a fixed
template. Swap RuleBasedProvider for an LLM-backed provider later and this
file becomes reference logic / a fallback rather than the primary path.

Sprint 1 changes:
- Workout day count now exactly matches the user's selected
  `workouts_per_week_current` (previously blended with an experience-based
  default, which is why day counts sometimes didn't match onboarding).
- Adaptive fatigue (intensity_modifier < 0) now reduces volume (sets) only,
  never the day count — reducing days was what caused the mismatch bug.
- BMI is calculated and used as a soft preference for lower-impact exercises.
- Medical conditions (not just injuries) now exclude contraindicated exercises.
- `cleared_for_exercise = False` caps the plan to a conservative, low-impact,
  lower-volume mode rather than generating a normal-intensity plan.
- Exercise selection is seeded per-user (so two users with identical profiles
  get different plans) and per-regeneration (so clicking "regenerate" gives a
  genuinely different plan, not a repeat), while remaining stable between
  simple page reloads of the same plan.
- Selected exercises are ordered compound-first, then isolation.
"""
import random

from app.data.exercise_library import exercises_for, LEVEL_RANK

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Layout for every possible day count, not just 2-6, so any onboarding
# selection (including edge cases like 1 or 7) is honored exactly.
TRAINING_DAY_LAYOUT = {
    1: [0],
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 3, 4],
    6: [0, 1, 2, 3, 4, 5],
    7: [0, 1, 2, 3, 4, 5, 6],
}

SPLIT_BY_EXPERIENCE = {
    "beginner": ["full_body"],
    "intermediate": ["push", "lower_body", "pull"],
    "advanced": ["push", "pull", "lower_body"],
}

GOAL_PARAMS = {
    "build_muscle": {"sets": 4, "reps": "8-12", "rest_seconds": 90, "seconds_per_rep": 3.5},
    "lose_weight": {"sets": 3, "reps": "12-15", "rest_seconds": 45, "seconds_per_rep": 3},
    "improve_endurance": {"sets": 3, "reps": "15-20", "rest_seconds": 30, "seconds_per_rep": 2.5},
    "general_health": {"sets": 3, "reps": "10-12", "rest_seconds": 60, "seconds_per_rep": 3},
    "sport_specific": {"sets": 3, "reps": "8-12", "rest_seconds": 60, "seconds_per_rep": 3},
}

EXERCISES_PER_DAY = 5
CONSERVATIVE_EXERCISES_PER_DAY = 3
CONSERVATIVE_MAX_TRAINING_DAYS = 3


def _estimate_duration_minutes(exercise_count: int, params: dict) -> int:
    reps_low = int(params["reps"].split("-")[0])
    per_set_seconds = reps_low * params["seconds_per_rep"] + params["rest_seconds"]
    total_seconds = exercise_count * params["sets"] * per_set_seconds
    return max(15, round(total_seconds / 60))


def _calculate_bmi(weight_kg: float, height_cm: float) -> float | None:
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def _order_and_select(pool: list, count: int, rng: random.Random, avoid_names: set) -> list:
    """
    Shuffles deterministically (per the caller's seeded rng), prefers
    exercises not used in the immediately previous plan when enough
    alternatives exist, then sorts compound-first for a sensible session order.
    """
    if not pool:
        return []

    shuffled = pool[:]
    rng.shuffle(shuffled)

    fresh = [ex for ex in shuffled if ex["name"] not in avoid_names]
    ordered_candidates = fresh + [ex for ex in shuffled if ex["name"] in avoid_names]

    selected = ordered_candidates[:count]
    selected.sort(key=lambda ex: ex.get("order_priority", 2))
    return selected


def build_workout_plan(context: dict) -> dict:
    fitness = context.get("fitness_experience") or {}
    goals = context.get("goals") or {}
    medical = context.get("medical") or {}
    body = context.get("body_metrics") or {}
    intensity_modifier = context.get("intensity_modifier", 0)  # -1, 0, or +1 from the adaptive engine
    variation_seed = context.get("variation_seed", "default")
    avoid_exercise_names = set(context.get("avoid_exercise_names") or [])

    experience = fitness.get("experience_level", "beginner")
    equipment = fitness.get("equipment_access", "none")
    preferred_types = set(fitness.get("preferred_workout_types") or [])
    injuries = set(medical.get("injuries") or [])
    conditions = set(medical.get("conditions") or [])
    cleared_for_exercise = medical.get("cleared_for_exercise", True)
    primary_goal = goals.get("primary_goal", "general_health")

    # Exactly the user's selected training frequency — this is the Sprint 1
    # fix for day counts not matching onboarding. Experience/goal influence
    # exercise selection and volume, never how many days are generated.
    requested_days = fitness.get("workouts_per_week_current")
    training_day_count = max(1, min(7, int(requested_days))) if requested_days else 3

    if not cleared_for_exercise:
        training_day_count = min(training_day_count, CONSERVATIVE_MAX_TRAINING_DAYS)

    training_indices = set(TRAINING_DAY_LAYOUT.get(training_day_count, TRAINING_DAY_LAYOUT[3]))

    bmi = _calculate_bmi(body.get("weight_kg"), body.get("height_cm"))
    prefer_low_impact = not cleared_for_exercise or (bmi is not None and bmi >= 30)

    split = SPLIT_BY_EXPERIENCE.get(experience, SPLIT_BY_EXPERIENCE["beginner"])
    params = dict(GOAL_PARAMS.get(primary_goal, GOAL_PARAMS["general_health"]))
    params["sets"] = max(2, min(5, params["sets"] + intensity_modifier))

    if not cleared_for_exercise:
        params["sets"] = min(params["sets"], 2)

    exercises_per_day = CONSERVATIVE_EXERCISES_PER_DAY if not cleared_for_exercise else EXERCISES_PER_DAY
    wants_cardio = "cardio" in preferred_types or primary_goal == "improve_endurance"
    wants_yoga = "yoga" in preferred_types

    rng = random.Random(f"{variation_seed}:workout")

    schedule = []
    split_cursor = 0
    yoga_assigned = False

    for i, day_name in enumerate(DAY_NAMES):
        if i in training_indices:
            focus = split[split_cursor % len(split)]
            split_cursor += 1

            pool = exercises_for(focus, equipment, injuries, conditions, prefer_low_impact)
            selected = _order_and_select(pool, exercises_per_day, rng, avoid_exercise_names)

            if wants_cardio and cleared_for_exercise:
                cardio_pool = exercises_for("cardio", equipment, injuries, conditions, prefer_low_impact)
                cardio_pick = _order_and_select(cardio_pool, 1, rng, avoid_exercise_names)
                if cardio_pick:
                    selected = (selected[:-1] if len(selected) >= exercises_per_day else selected) + cardio_pick

            exercises = [
                {
                    "name": ex["name"],
                    "sets": params["sets"],
                    "reps": params["reps"],
                    "rest_seconds": params["rest_seconds"],
                    "instructions": ex["instructions"],
                }
                for ex in selected
            ]

            schedule.append({
                "day_name": day_name,
                "is_rest_day": False,
                "focus": focus,
                "exercises": exercises,
                "estimated_duration_minutes": _estimate_duration_minutes(len(exercises), params) if exercises else 0,
            })
        elif wants_yoga and not yoga_assigned and cleared_for_exercise:
            yoga_pool = exercises_for("yoga", equipment, injuries, conditions)
            yoga_pick = _order_and_select(yoga_pool, 3, rng, avoid_exercise_names)
            yoga_assigned = True
            exercises = [
                {
                    "name": ex["name"],
                    "sets": 1,
                    "reps": "60 seconds",
                    "rest_seconds": 15,
                    "instructions": ex["instructions"],
                }
                for ex in yoga_pick
            ]
            schedule.append({
                "day_name": day_name,
                "is_rest_day": False,
                "focus": "yoga",
                "exercises": exercises,
                "estimated_duration_minutes": max(15, len(exercises) * 3),
            })
        else:
            schedule.append({
                "day_name": day_name,
                "is_rest_day": True,
                "focus": "rest",
                "exercises": [],
                "estimated_duration_minutes": 0,
            })

    return {"schedule": schedule, "bmi": bmi}
