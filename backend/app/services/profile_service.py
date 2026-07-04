from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.services import onboarding_service, medical_history_service, notification_service


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
    db.commit()
    db.refresh(user)
    notification_service.create_notification(db, user, "profile_updated", "Your profile information was updated.")
    return get_profile(db, user)
