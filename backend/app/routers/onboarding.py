from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.onboarding import OnboardingUpsertRequest, OnboardingResponse
from app.services import onboarding_service

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.get("", response_model=OnboardingResponse)
def get_onboarding(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    profile = onboarding_service.get_onboarding(db, current_user)
    return OnboardingResponse(
        goals=profile.goals,
        body_metrics=profile.body_metrics,
        fitness_experience=profile.fitness_experience,
        lifestyle_diet=profile.lifestyle_diet,
        is_complete=current_user.has_completed_onboarding,
    )


@router.post("", response_model=OnboardingResponse)
def save_onboarding(
    payload: OnboardingUpsertRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = onboarding_service.upsert_onboarding(db, current_user, payload)
    return OnboardingResponse(
        goals=profile.goals,
        body_metrics=profile.body_metrics,
        fitness_experience=profile.fitness_experience,
        lifestyle_diet=profile.lifestyle_diet,
        is_complete=current_user.has_completed_onboarding,
    )
