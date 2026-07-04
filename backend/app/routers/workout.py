from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.workout import WorkoutPlanResponse, WorkoutCompletionRequest, WorkoutCompletionResponse
from app.services import workout_service

router = APIRouter(prefix="/workout", tags=["workout"])


@router.get("", response_model=WorkoutPlanResponse)
def get_current_workout_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = workout_service.get_or_create_current_plan(db, current_user)
    return WorkoutPlanResponse.model_validate(plan)


@router.post("/regenerate", response_model=WorkoutPlanResponse)
def regenerate_workout_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = workout_service.regenerate_current_plan(db, current_user)
    return WorkoutPlanResponse.model_validate(plan)


@router.get("/completions")
def get_completions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = workout_service.get_or_create_current_plan(db, current_user)
    return workout_service.get_completions_for_plan(db, current_user, plan)


@router.post("/completions", response_model=WorkoutCompletionResponse)
def save_completion(
    payload: WorkoutCompletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        record = workout_service.record_completion(db, current_user, payload.workout_date, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return WorkoutCompletionResponse.model_validate(record)
