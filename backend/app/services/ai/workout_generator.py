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

Sprint 4 (Personalization Engine) changes — every one of these is optional
and falls back to the Sprint 1-3 behavior when the user hasn't set a
Workout Preference yet, so existing users see no change until they visit
Workout Preferences:
- `workout_style` (Strength/Hypertrophy/Fat Loss/Cardio/Calisthenics/...)
  overrides the goal-derived sets/reps/rest scheme when set.
- `equipment_available` (multi-select) is a *hard* filter via
  exercise_library.exercises_for's `equipment_tags` param — "Home +
  Bodyweight Only" genuinely excludes Bench Press / Lat Pulldown / Cable Fly
  rather than just relying on the coarse equipment tier.
- `disliked_exercises` and free-text `avoid_movements` ("no overhead press",
  "bad knees") are hard-excluded from every pool.
- `liked_exercises` are boosted to the front of selection (still shuffled
  among themselves and never forced if incompatible with equipment/injury).
- `preferred_duration_minutes` maps to how many exercises are scheduled per
  day.
- `workout_intensity` (light/moderate/high) adds to the sets on top of the
  existing adaptive intensity_modifier.
- `favorite_muscle_groups` reorders the day-split so favored focuses recur
  more often across the week.
- `exercise_replacement_memory` (Sprint 4 objective 5): once the user has
  replaced an exercise with the same alternative 2+ times, that alternative
  is substituted automatically going forward, provided it's still valid for
  the user's current equipment/injuries.
"""
import random

from app.data.exercise_library import exercises_for, find_exercise_by_name

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

# Sprint 4: Workout Preferences "Preferred Workout Style" overrides GOAL_PARAMS
# when set. Keys match the snake_case values the frontend sends.
STYLE_PARAMS = {
    "strength": {"sets": 5, "reps": "3-6", "rest_seconds": 150, "seconds_per_rep": 4},
    "powerlifting": {"sets": 5, "reps": "1-5", "rest_seconds": 180, "seconds_per_rep": 5},
    "hypertrophy": {"sets": 4, "reps": "8-12", "rest_seconds": 75, "seconds_per_rep": 3.5},
    "muscle_gain": {"sets": 4, "reps": "8-12", "rest_seconds": 75, "seconds_per_rep": 3.5},
    "fat_loss": {"sets": 3, "reps": "12-15", "rest_seconds": 40, "seconds_per_rep": 3},
    "cardio": {"sets": 3, "reps": "15-20", "rest_seconds": 30, "seconds_per_rep": 2.5},
    "functional_training": {"sets": 3, "reps": "10-15", "rest_seconds": 45, "seconds_per_rep": 3},
    "calisthenics": {"sets": 3, "reps": "8-15", "rest_seconds": 60, "seconds_per_rep": 3},
}

# Sprint 4: "Preferred Workout Duration" maps to how many exercises are
# scheduled in a training day — a rough but effective duration lever, since
# actual duration is estimated from exercise count x sets x reps x rest.
DURATION_TO_EXERCISE_COUNT = {20: 3, 30: 4, 45: 5, 60: 6, 90: 8}

INTENSITY_PREFERENCE_OFFSET = {"light": -1, "moderate": 0, "high": 1}

MUSCLE_GROUP_TO_FOCUS = {
    "chest": "push", "shoulders": "push", "triceps": "push",
    "back": "pull", "biceps": "pull", "lats": "pull",
    "legs": "lower_body", "glutes": "lower_body", "quads": "lower_body",
    "hamstrings": "lower_body", "calves": "lower_body",
    "core": "full_body", "abs": "full_body", "full_body": "full_body",
}

# Sprint 4: "Injuries / Movements To Avoid" free text ("No overhead press",
# "Bad knees", "Shoulder pain") is matched against these keywords rather than
# requiring the exact injury vocabulary medical history uses, since this
# field is meant to be typed in plain language.
AVOID_TEXT_TO_INJURY_TAGS = {
    "knee": {"left_knee", "right_knee"},
    "shoulder": {"shoulder"},
    "overhead": {"shoulder"},
    "back": {"lower_back"},
    "spine": {"lower_back"},
    "ankle": {"ankle"},
}
AVOID_TEXT_MOVEMENT_KEYWORDS = ["squat", "deadlift", "lunge", "press", "pull-up", "pullup", "burpee", "jump", "row"]

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


def _closest_duration_key(duration_minutes: int) -> int:
    return min(DURATION_TO_EXERCISE_COUNT.keys(), key=lambda d: abs(d - duration_minutes))


def _equipment_tags_from_preferences(equipment_available: list) -> set:
    """
    Maps the Workout Preferences "Equipment Available" multi-select labels
    (as sent by the frontend, snake_case) onto the tags exercise_library.py
    infers from exercise names.
    """
    mapping = {
        "dumbbells": "dumbbells",
        "barbell": "barbell",
        "resistance_bands": "resistance_bands",
        "machines": "machines",
        "pull_up_bar": "pull_up_bar",
        "bench": "bench",
        "bodyweight_only": "bodyweight_only",
    }
    return {mapping[e] for e in equipment_available if e in mapping}


def _parse_avoid_movements(avoid_movements: list) -> tuple:
    """Free-text 'no overhead press' / 'bad knees' -> (injury_tags, name-keyword excludes)."""
    injury_tags = set()
    name_keywords = set()
    for text in avoid_movements or []:
        low = text.lower()
        for keyword, tags in AVOID_TEXT_TO_INJURY_TAGS.items():
            if keyword in low:
                injury_tags |= tags
        for keyword in AVOID_TEXT_MOVEMENT_KEYWORDS:
            if keyword in low:
                name_keywords.add(keyword)
    return injury_tags, name_keywords


def _pool_with_fallback(
    focus: str, equipment: str, medical_injuries: set, avoid_injury_tags: set, conditions: set, prefer_low_impact: bool,
    equipment_tags: set, hard_excluded_names: set, avoid_name_keywords: set,
) -> list:
    """
    exercises_for()'s filters are individually safe (each is documented to
    never empty a *reasonable* pool), but stacking several optional Sprint 4
    preferences together — e.g. free-text "avoid movements" mapping to an
    injury tag, combined with a narrow focus — can legitimately empty a
    single focus's pool. Rather than silently generating a training day with
    zero exercises, this widens the search in three safe steps:
      1) exact filters: equipment tags + medical injuries + avoid-movement
         injury tags + avoid-movement name keywords
      2) drop the avoid-movement name-keyword filter only
      3) also drop the avoid-movement injury tags (medical injuries and
         equipment_tags are NEVER dropped — equipment is an explicit hard
         preference and medical injuries are a hard safety constraint)
    The caller falls back to "full_body" and then to a rest day only if all
    three still come up empty, which in practice only happens for a nearly-
    empty equipment/injury combination the library doesn't cover at all.
    """
    pool = exercises_for(
        focus, equipment, medical_injuries | avoid_injury_tags, conditions, prefer_low_impact,
        equipment_tags=equipment_tags, exclude_names=hard_excluded_names,
    )
    pool = [ex for ex in pool if not any(kw in ex["name"].lower() for kw in avoid_name_keywords)]
    if pool:
        return pool

    pool = exercises_for(
        focus, equipment, medical_injuries | avoid_injury_tags, conditions, prefer_low_impact,
        equipment_tags=equipment_tags, exclude_names=hard_excluded_names,
    )
    if pool:
        return pool

    return exercises_for(
        focus, equipment, medical_injuries, conditions, prefer_low_impact,
        equipment_tags=equipment_tags, exclude_names=hard_excluded_names,
    )


def _order_and_select(pool: list, count: int, rng: random.Random, avoid_names: set, liked_names: set) -> list:
    """
    Shuffles deterministically (per the caller's seeded rng), boosts liked
    exercises to the front (Sprint 4), then prefers exercises not used in the
    immediately previous plan when enough alternatives exist, then sorts
    compound-first for a sensible session order.
    """
    if not pool:
        return []

    shuffled = pool[:]
    rng.shuffle(shuffled)

    if liked_names:
        shuffled.sort(key=lambda ex: 0 if ex["name"] in liked_names else 1)

    fresh = [ex for ex in shuffled if ex["name"] not in avoid_names]
    ordered_candidates = fresh + [ex for ex in shuffled if ex["name"] in avoid_names]

    selected = ordered_candidates[:count]
    selected.sort(key=lambda ex: ex.get("order_priority", 2))
    return selected


def _apply_replacement_memory(
    selected: list, dominant_map: dict, equipment_tags: set, injuries: set, conditions: set, already_used: set
) -> list:
    """
    Sprint 4 objective 5 (User Preference Memory): substitutes any exercise
    that the user has repeatedly replaced with the same alternative, as long
    as that alternative is still compatible with current equipment/injuries
    and isn't already scheduled that day.
    """
    if not dominant_map:
        return selected

    result = []
    for ex in selected:
        replacement_name = dominant_map.get(ex["name"])
        if replacement_name and replacement_name not in already_used:
            replacement = find_exercise_by_name(replacement_name)
            is_compatible = (
                replacement is not None
                and not (set(replacement["injury_tags"]) & injuries)
                and not (set(replacement.get("contraindications", [])) & conditions)
                and (not equipment_tags or (replacement["equipment_tags"] & (equipment_tags | {"bodyweight_only"})))
            )
            if is_compatible:
                result.append(replacement)
                already_used.add(replacement_name)
                continue
        result.append(ex)
        already_used.add(ex["name"])
    return result


def build_workout_plan(context: dict) -> dict:
    fitness = context.get("fitness_experience") or {}
    goals = context.get("goals") or {}
    medical = context.get("medical") or {}
    body = context.get("body_metrics") or {}
    preferences = context.get("preferences") or {}
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

    # --- Sprint 4: preference-derived signals ---
    workout_style = preferences.get("workout_style")
    equipment_tags = _equipment_tags_from_preferences(preferences.get("equipment_available") or [])
    liked_names = set(preferences.get("liked_exercises") or [])
    disliked_names = set(preferences.get("disliked_exercises") or [])
    avoid_injury_tags, avoid_name_keywords = _parse_avoid_movements(preferences.get("avoid_movements") or [])
    hard_excluded_names = avoid_exercise_names | disliked_names
    intensity_preference_offset = INTENSITY_PREFERENCE_OFFSET.get(preferences.get("workout_intensity"), 0)
    favorite_muscle_groups = preferences.get("favorite_muscle_groups") or []
    dominant_replacements = preferences.get("dominant_replacements") or {}

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

    split = list(SPLIT_BY_EXPERIENCE.get(experience, SPLIT_BY_EXPERIENCE["beginner"]))

    # Sprint 4: favorite muscle groups recur more often in the weekly split.
    favorite_focuses = [
        MUSCLE_GROUP_TO_FOCUS[g.lower()] for g in favorite_muscle_groups if g.lower() in MUSCLE_GROUP_TO_FOCUS
    ]
    if favorite_focuses:
        split = favorite_focuses + [f for f in split if f not in favorite_focuses] + split

    if workout_style == "cardio":
        split = ["cardio"]

    if workout_style in STYLE_PARAMS:
        params = dict(STYLE_PARAMS[workout_style])
    else:
        params = dict(GOAL_PARAMS.get(primary_goal, GOAL_PARAMS["general_health"]))

    total_intensity_adjustment = intensity_modifier + intensity_preference_offset
    params["sets"] = max(2, min(6, params["sets"] + total_intensity_adjustment))

    if not cleared_for_exercise:
        params["sets"] = min(params["sets"], 2)

    if preferences.get("preferred_duration_minutes"):
        exercises_per_day = DURATION_TO_EXERCISE_COUNT[_closest_duration_key(preferences["preferred_duration_minutes"])]
    else:
        exercises_per_day = EXERCISES_PER_DAY
    if not cleared_for_exercise:
        exercises_per_day = min(exercises_per_day, CONSERVATIVE_EXERCISES_PER_DAY)

    wants_cardio = "cardio" in preferred_types or primary_goal == "improve_endurance" or workout_style == "cardio"
    wants_yoga = "yoga" in preferred_types

    rng = random.Random(f"{variation_seed}:workout")

    schedule = []
    split_cursor = 0
    yoga_assigned = False

    for i, day_name in enumerate(DAY_NAMES):
        if i in training_indices:
            focus = split[split_cursor % len(split)]
            split_cursor += 1

            pool = _pool_with_fallback(
                focus, equipment, injuries, avoid_injury_tags, conditions, prefer_low_impact,
                equipment_tags, hard_excluded_names, avoid_name_keywords,
            )
            if not pool and focus != "full_body":
                # Sprint 4: last-resort fallback when a single focus is
                # entirely incompatible with the user's equipment/injury
                # combination — full_body pulls from a broader movement set.
                pool = _pool_with_fallback(
                    "full_body", equipment, injuries, avoid_injury_tags, conditions, prefer_low_impact,
                    equipment_tags, hard_excluded_names, avoid_name_keywords,
                )
            selected = _order_and_select(pool, exercises_per_day, rng, avoid_exercise_names, liked_names)

            if not selected:
                # Truly nothing valid for this day given the current
                # preferences — a genuinely empty active day is worse than a
                # rest day; the user can adjust preferences if this recurs.
                schedule.append({
                    "day_name": day_name, "is_rest_day": True, "focus": "rest",
                    "exercises": [], "estimated_duration_minutes": 0,
                })
                continue

            if wants_cardio and cleared_for_exercise and focus != "cardio":
                cardio_pool = _pool_with_fallback(
                    "cardio", equipment, injuries, avoid_injury_tags, conditions, prefer_low_impact,
                    equipment_tags, hard_excluded_names, avoid_name_keywords,
                )
                cardio_pick = _order_and_select(cardio_pool, 1, rng, avoid_exercise_names, liked_names)
                if cardio_pick:
                    selected = (selected[:-1] if len(selected) >= exercises_per_day else selected) + cardio_pick

            used_names = {ex["name"] for ex in selected}
            selected = _apply_replacement_memory(selected, dominant_replacements, equipment_tags, injuries | avoid_injury_tags, conditions, used_names)

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
            yoga_pool = exercises_for("yoga", equipment, injuries, conditions, exclude_names=hard_excluded_names)
            yoga_pick = _order_and_select(yoga_pool, 3, rng, avoid_exercise_names, liked_names)
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
