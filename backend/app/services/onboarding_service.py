from sqlalchemy.orm import Session

from app.models.onboarding import OnboardingProfile
from app.models.user import User
from app.schemas.onboarding import OnboardingUpsertRequest


def _get_or_create_profile(db: Session, user: User) -> OnboardingProfile:
    profile = db.query(OnboardingProfile).filter(OnboardingProfile.user_id == user.id).first()
    if profile is None:
        profile = OnboardingProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def _is_complete(profile: OnboardingProfile) -> bool:
    return all(
        [profile.goals, profile.body_metrics, profile.fitness_experience, profile.lifestyle_diet]
    )


def get_onboarding(db: Session, user: User) -> OnboardingProfile:
    return _get_or_create_profile(db, user)


def upsert_onboarding(db: Session, user: User, payload: OnboardingUpsertRequest) -> OnboardingProfile:
    profile = _get_or_create_profile(db, user)

    if payload.goals is not None:
        profile.goals = payload.goals.model_dump()
    if payload.body_metrics is not None:
        profile.body_metrics = payload.body_metrics.model_dump()
    if payload.fitness_experience is not None:
        profile.fitness_experience = payload.fitness_experience.model_dump()
    if payload.lifestyle_diet is not None:
        profile.lifestyle_diet = payload.lifestyle_diet.model_dump()

    db.commit()
    db.refresh(profile)

    if _is_complete(profile) and not user.has_completed_onboarding:
        user.has_completed_onboarding = True
        db.commit()

    return profile
