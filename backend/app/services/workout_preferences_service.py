from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout_preferences import WorkoutPreferences
from app.schemas.preferences import WorkoutPreferencesUpdateRequest

UPDATABLE_FIELDS = [
    "workout_style",
    "workout_location",
    "equipment_available",
    "preferred_duration_minutes",
    "workout_intensity",
    "preferred_workout_time",
    "favorite_muscle_groups",
    "liked_exercises",
    "disliked_exercises",
    "avoid_movements",
]

# A replacement pattern needs to repeat at least this many times before
# future plans automatically favor it (Sprint 4 objective 5) — a single
# one-off swap shouldn't permanently change what gets generated.
REPLACEMENT_MEMORY_THRESHOLD = 2


def get_or_create_preferences(db: Session, user: User) -> WorkoutPreferences:
    prefs = db.query(WorkoutPreferences).filter(WorkoutPreferences.user_id == user.id).first()
    if prefs is None:
        prefs = WorkoutPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


def update_preferences(db: Session, user: User, payload: WorkoutPreferencesUpdateRequest) -> WorkoutPreferences:
    prefs = get_or_create_preferences(db, user)
    data = payload.model_dump(exclude_unset=True)
    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(prefs, field, data[field])
    db.commit()
    db.refresh(prefs)
    return prefs


def record_exercise_replacement(db: Session, user: User, original_name: str, replacement_name: str) -> None:
    """Sprint 4 objective 5: increments the remembered replacement count for
    `original_name` -> `replacement_name`. Called every time a user replaces
    or swaps an exercise, whether manually chosen or auto-swapped."""
    if original_name == replacement_name:
        return
    prefs = get_or_create_preferences(db, user)
    memory = dict(prefs.exercise_replacement_memory or {})
    counts = dict(memory.get(original_name, {}))
    counts[replacement_name] = counts.get(replacement_name, 0) + 1
    memory[original_name] = counts
    prefs.exercise_replacement_memory = memory
    db.commit()


def dominant_replacements(replacement_memory: dict) -> dict[str, str]:
    """
    Reduces the full {original: {replacement: count}} memory down to just the
    dominant replacement per original exercise, for exercises replaced at
    least REPLACEMENT_MEMORY_THRESHOLD times. Used by workout_generator.py to
    proactively substitute before the user even asks again.
    """
    result = {}
    for original, counts in (replacement_memory or {}).items():
        if not counts:
            continue
        best_replacement, best_count = max(counts.items(), key=lambda item: item[1])
        if best_count >= REPLACEMENT_MEMORY_THRESHOLD:
            result[original] = best_replacement
    return result
