"""
Deterministic workout plan builder. This is the `builder` function passed to
RuleBasedProvider — see provider.py for why this is structured this way.
Everything here is derived from the user's actual profile; nothing is a fixed
template. Swap RuleBasedProvider for an LLM-backed provider later and this
file becomes reference logic / a fallback rather than the primary path.
"""
import math

from app.data.exercise_library import exercises_for

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

TRAINING_DAY_LAYOUT = {
    2: [0, 3],
    3: [0, 2, 4],
    4: [0, 1, 3, 4],
    5: [0, 1, 2, 3, 4],
    6: [0, 1, 2, 3, 4, 5],
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


def _estimate_duration_minutes(exercise_count: int, params: dict) -> int:
    reps_low = int(params["reps"].split("-")[0])
    per_set_seconds = reps_low * params["seconds_per_rep"] + params["rest_seconds"]
    total_seconds = exercise_count * params["sets"] * per_set_seconds
    return max(15, round(total_seconds / 60))


def build_workout_plan(context: dict) -> dict:
    fitness = context.get("fitness_experience") or {}
    goals = context.get("goals") or {}
    medical = context.get("medical") or {}
    intensity_modifier = context.get("intensity_modifier", 0)  # -1, 0, or +1 from the adaptive engine

    experience = fitness.get("experience_level", "beginner")
    equipment = fitness.get("equipment_access", "none")
    preferred_types = set(fitness.get("preferred_workout_types") or [])
    injuries = set(medical.get("injuries") or [])
    primary_goal = goals.get("primary_goal", "general_health")
    current_freq = fitness.get("workouts_per_week_current") or 0

    base_days = {"beginner": 3, "intermediate": 4, "advanced": 5}.get(experience, 3)
    training_day_count = max(2, min(6, round((base_days + max(current_freq, base_days)) / 2)))
    if intensity_modifier < 0:
        training_day_count = max(2, training_day_count - 1)  # back off when fatigued
    training_indices = set(TRAINING_DAY_LAYOUT.get(training_day_count, TRAINING_DAY_LAYOUT[3]))

    split = SPLIT_BY_EXPERIENCE.get(experience, SPLIT_BY_EXPERIENCE["beginner"])
    params = dict(GOAL_PARAMS.get(primary_goal, GOAL_PARAMS["general_health"]))
    params["sets"] = max(2, min(5, params["sets"] + intensity_modifier))  # adaptive volume adjustment
    wants_cardio = "cardio" in preferred_types or primary_goal == "improve_endurance"
    wants_yoga = "yoga" in preferred_types

    schedule = []
    split_cursor = 0
    yoga_assigned = False

    for i, day_name in enumerate(DAY_NAMES):
        if i in training_indices:
            focus = split[split_cursor % len(split)]
            split_cursor += 1

            pool = exercises_for(focus, equipment, injuries)
            selected = pool[:EXERCISES_PER_DAY] if pool else []

            if wants_cardio:
                cardio_pool = exercises_for("cardio", equipment, injuries)
                if cardio_pool:
                    selected = selected[:-1] + [cardio_pool[0]] if len(selected) >= EXERCISES_PER_DAY else selected + [cardio_pool[0]]

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
        elif wants_yoga and not yoga_assigned:
            yoga_pool = exercises_for("yoga", equipment, injuries)
            yoga_assigned = True
            exercises = [
                {
                    "name": ex["name"],
                    "sets": 1,
                    "reps": "60 seconds",
                    "rest_seconds": 15,
                    "instructions": ex["instructions"],
                }
                for ex in yoga_pool
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

    return {"schedule": schedule}
