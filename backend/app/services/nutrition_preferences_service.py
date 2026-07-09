from sqlalchemy.orm import Session

from app.models.user import User
from app.models.nutrition_preferences import NutritionPreferences
from app.schemas.preferences import NutritionPreferencesUpdateRequest

UPDATABLE_FIELDS = [
    "diet_type",
    "cuisine_preference",
    "budget",
    "meals_per_day",
    "favorite_foods",
    "disliked_foods",
    "allergies",
    "water_goal_ml",
    "preferred_snacks",
    "cooking_time_preference",
]

REPLACEMENT_MEMORY_THRESHOLD = 2


def get_or_create_preferences(db: Session, user: User) -> NutritionPreferences:
    prefs = db.query(NutritionPreferences).filter(NutritionPreferences.user_id == user.id).first()
    if prefs is None:
        prefs = NutritionPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


def update_preferences(db: Session, user: User, payload: NutritionPreferencesUpdateRequest) -> NutritionPreferences:
    prefs = get_or_create_preferences(db, user)
    data = payload.model_dump(exclude_unset=True)
    for field in UPDATABLE_FIELDS:
        if field in data:
            setattr(prefs, field, data[field])
    db.commit()
    db.refresh(prefs)
    return prefs


def record_meal_replacement(db: Session, user: User, original_name: str, replacement_name: str) -> None:
    if original_name == replacement_name:
        return
    prefs = get_or_create_preferences(db, user)
    memory = dict(prefs.meal_replacement_memory or {})
    counts = dict(memory.get(original_name, {}))
    counts[replacement_name] = counts.get(replacement_name, 0) + 1
    memory[original_name] = counts
    prefs.meal_replacement_memory = memory
    db.commit()


def dominant_replacements(replacement_memory: dict) -> dict[str, str]:
    result = {}
    for original, counts in (replacement_memory or {}).items():
        if not counts:
            continue
        best_replacement, best_count = max(counts.items(), key=lambda item: item[1])
        if best_count >= REPLACEMENT_MEMORY_THRESHOLD:
            result[original] = best_replacement
    return result
