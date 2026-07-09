from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.preferences import (
    WorkoutPreferencesResponse,
    WorkoutPreferencesUpdateRequest,
    NutritionPreferencesResponse,
    NutritionPreferencesUpdateRequest,
)
from app.services import workout_preferences_service, nutrition_preferences_service

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/workout", response_model=WorkoutPreferencesResponse)
def get_workout_preferences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return workout_preferences_service.get_or_create_preferences(db, current_user)


@router.put("/workout", response_model=WorkoutPreferencesResponse)
def update_workout_preferences(
    payload: WorkoutPreferencesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return workout_preferences_service.update_preferences(db, current_user, payload)


@router.get("/nutrition", response_model=NutritionPreferencesResponse)
def get_nutrition_preferences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return nutrition_preferences_service.get_or_create_preferences(db, current_user)


@router.put("/nutrition", response_model=NutritionPreferencesResponse)
def update_nutrition_preferences(
    payload: NutritionPreferencesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return nutrition_preferences_service.update_preferences(db, current_user, payload)
