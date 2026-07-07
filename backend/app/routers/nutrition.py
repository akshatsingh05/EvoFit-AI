from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.nutrition import (
    NutritionPlanResponse,
    NutritionWeekResponse,
    NutritionWeekPlanResponse,
    MealCompletionRequest,
    MealCompletionResponse,
)
from app.schemas.history import HistoryListResponse
from app.services import nutrition_service

router = APIRouter(prefix="/nutrition", tags=["nutrition"])


@router.get("", response_model=NutritionPlanResponse)
def get_today_nutrition_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Kept for backward compatibility (Dashboard, etc.) — always resolves to today."""
    plan = nutrition_service.get_or_create_today_plan(db, current_user)
    return NutritionPlanResponse.model_validate(plan)


@router.post("/regenerate", response_model=NutritionPlanResponse)
def regenerate_nutrition_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = nutrition_service.regenerate_today_plan(db, current_user)
    return NutritionPlanResponse.model_validate(plan)


@router.get("/week", response_model=NutritionWeekResponse)
def get_nutrition_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """offset=0 is the current week, negative is past, positive is future."""
    week_start_date = nutrition_service.week_start_for_offset(offset)
    before_registration = nutrition_service.is_week_before_registration(week_start_date, current_user)
    plan = nutrition_service.get_plan_for_week(db, current_user, week_start_date)

    return NutritionWeekResponse(
        week_start_date=week_start_date,
        offset=offset,
        is_before_registration=before_registration,
        plan=NutritionWeekPlanResponse.model_validate(plan) if plan else None,
        plan_info=nutrition_service.build_plan_info(db, current_user, plan) if plan else None,
    )


@router.post("/week/regenerate", response_model=NutritionWeekResponse)
def regenerate_nutrition_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start_date = nutrition_service.week_start_for_offset(offset)
    try:
        plan = nutrition_service.regenerate_plan_for_week(db, current_user, week_start_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return NutritionWeekResponse(
        week_start_date=week_start_date,
        offset=offset,
        is_before_registration=False,
        plan=NutritionWeekPlanResponse.model_validate(plan),
        plan_info=nutrition_service.build_plan_info(db, current_user, plan),
    )


@router.get("/history", response_model=HistoryListResponse)
def get_nutrition_history(
    limit: int = 12, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    entries = nutrition_service.get_nutrition_history_entries(db, current_user, limit)
    return HistoryListResponse(kind="nutrition", entries=entries)


@router.get("/completions/week")
def get_completions_for_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start_date = nutrition_service.week_start_for_offset(offset)
    return nutrition_service.get_completions_for_week(db, current_user, week_start_date)


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
