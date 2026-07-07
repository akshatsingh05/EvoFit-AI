from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutCompletion
from app.models.nutrition import NutritionPlan, MealCompletion
from app.models.notification import Notification
from app.models.daily_checkin import DailyCheckIn
from app.models.adaptive_insight import AdaptiveInsight
from app.models.progress import WeightLog
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services import onboarding_service, medical_history_service, notification_service

# Registry of "owns rows keyed by user_id" models that aren't already covered
# by an ORM cascade off User (see models/user.py: onboarding_profile,
# medical_history, and settings cascade automatically via relationship()).
# Delete Account iterates this list; a future "Export My Data" feature can
# reuse the exact same registry to serialize everything instead of deleting it.
USER_OWNED_MODELS = [
    WorkoutCompletion,
    WorkoutPlan,
    MealCompletion,
    NutritionPlan,
    Notification,
    DailyCheckIn,
    AdaptiveInsight,
    WeightLog,
]


def get_profile(db: Session, user: User) -> ProfileResponse:
    onboarding = onboarding_service.get_onboarding(db, user)
    medical = medical_history_service.get_medical_history(db, user)

    return ProfileResponse(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        has_completed_onboarding=user.has_completed_onboarding,
        goals=onboarding.goals,
        body_metrics=onboarding.body_metrics,
        fitness_experience=onboarding.fitness_experience,
        lifestyle_diet=onboarding.lifestyle_diet,
        medical_conditions=(medical.conditions if medical else []) or [],
        medical_injuries=(medical.injuries if medical else []) or [],
        medications=medical.medications if medical else None,
        allergies=medical.allergies if medical else None,
        cleared_for_exercise=medical.cleared_for_exercise if medical else None,
    )


def update_profile(db: Session, user: User, payload: ProfileUpdateRequest) -> ProfileResponse:
    user.full_name = payload.full_name.strip()

    if payload.email is not None:
        new_email = payload.email.lower()
        if new_email != user.email:
            existing = db.query(User).filter(User.email == new_email, User.id != user.id).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists"
                )
            user.email = new_email

    db.commit()
    db.refresh(user)
    notification_service.create_notification(db, user, "profile_updated", "Your profile information was updated.")
    return get_profile(db, user)


def delete_account(db: Session, user: User) -> None:
    """
    Permanently deletes the user and every row they own. onboarding_profile,
    medical_history, and settings cascade automatically via the User model's
    relationships; everything else is deleted explicitly via USER_OWNED_MODELS.
    """
    for model in USER_OWNED_MODELS:
        db.query(model).filter(model.user_id == user.id).delete(synchronize_session=False)

    db.delete(user)
    db.commit()
