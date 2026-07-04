from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.nutrition import NutritionPlanResponse, MealCompletionRequest, MealCompletionResponse
from app.services import nutrition_service

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("", response_model=NutritionPlanResponse)
def get_today_nutrition_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = nutrition_service.get_or_create_today_plan(db, current_user)
    return NutritionPlanResponse.model_validate(plan)


@router.post("/regenerate", response_model=NutritionPlanResponse)
def regenerate_nutrition_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = nutrition_service.regenerate_today_plan(db, current_user)
    return NutritionPlanResponse.model_validate(plan)


@router.get("/completions")
def get_completions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from datetime import date

    return nutrition_service.get_completions_for_date(db, current_user, date.today())


@router.post("/completions", response_model=MealCompletionResponse)
def save_completion(
    payload: MealCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = nutrition_service.record_meal_completion(
            db, current_user, payload.meal_date, payload.meal_type, payload.status
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return MealCompletionResponse.model_validate(record)
