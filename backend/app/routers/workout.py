from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.workout import (
    WorkoutPlanResponse,
    WorkoutWeekResponse,
    WorkoutCalendarResponse,
    WorkoutCompletionRequest,
    WorkoutCompletionResponse,
    ExerciseAlternativesResponse,
    ReplaceExerciseRequest,
)
from app.schemas.history import HistoryListResponse
from app.services import workout_service

router = APIRouter(prefix="/workout", tags=["workout"])


@router.get("", response_model=WorkoutPlanResponse)
def get_current_workout_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Kept for backward compatibility (Dashboard, etc.) — always resolves to the current week."""
    plan = workout_service.get_or_create_current_plan(db, current_user)
    return WorkoutPlanResponse.model_validate(plan)


@router.post("/regenerate", response_model=WorkoutPlanResponse)
def regenerate_workout_plan(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = workout_service.regenerate_current_plan(db, current_user)
    return WorkoutPlanResponse.model_validate(plan)


@router.get("/week", response_model=WorkoutWeekResponse)
def get_workout_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """offset=0 is the current week, negative is past, positive is future."""
    week_start_date = workout_service.week_start_for_offset(offset)
    before_registration = workout_service.is_week_before_registration(week_start_date, current_user)
    plan = workout_service.get_plan_for_week(db, current_user, week_start_date)

    return WorkoutWeekResponse(
        week_start_date=week_start_date,
        offset=offset,
        is_before_registration=before_registration,
        plan=WorkoutPlanResponse.model_validate(plan) if plan else None,
        plan_info=workout_service.build_plan_info(db, current_user, plan) if plan else None,
    )


@router.post("/week/regenerate", response_model=WorkoutWeekResponse)
def regenerate_workout_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start_date = workout_service.week_start_for_offset(offset)
    try:
        plan = workout_service.regenerate_plan_for_week(db, current_user, week_start_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return WorkoutWeekResponse(
        week_start_date=week_start_date,
        offset=offset,
        is_before_registration=False,
        plan=WorkoutPlanResponse.model_validate(plan),
        plan_info=workout_service.build_plan_info(db, current_user, plan),
    )


@router.get("/calendar", response_model=WorkoutCalendarResponse)
def get_workout_calendar(
    start: date_type,
    end: date_type,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if end < start:
        raise HTTPException(status_code=400, detail="end must not be before start")
    if (end - start).days > 62:
        raise HTTPException(status_code=400, detail="range too large; request at most ~2 months at a time")

    days = workout_service.get_calendar_data(db, current_user, start, end)
    streak = workout_service.compute_workout_streak(db, current_user)
    return WorkoutCalendarResponse(start_date=start, end_date=end, days=days, streak=streak)


@router.get("/history", response_model=HistoryListResponse)
def get_workout_history(
    limit: int = 12, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    entries = workout_service.get_workout_history_entries(db, current_user, limit)
    return HistoryListResponse(kind="workout", entries=entries)


@router.get("/completions/week")
def get_completions_for_week(
    offset: int = 0, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    week_start_date = workout_service.week_start_for_offset(offset)
    plan = workout_service.get_plan_for_week(db, current_user, week_start_date)
    return workout_service.get_completions_for_week(db, current_user, plan)


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


# --- Sprint 4: Plan Customization ---


@router.get("/week/exercise-alternatives", response_model=ExerciseAlternativesResponse)
def get_exercise_alternatives(
    day_index: int,
    exercise_index: int,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    week_start_date = workout_service.week_start_for_offset(offset)
    plan = workout_service.get_plan_for_week(db, current_user, week_start_date)
    if plan is None:
        raise HTTPException(status_code=404, detail="No plan exists for that week")
    try:
        alternatives = workout_service.get_exercise_alternatives(db, current_user, plan, day_index, exercise_index)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ExerciseAlternativesResponse(alternatives=alternatives)


@router.post("/week/replace-exercise", response_model=WorkoutWeekResponse)
def replace_exercise(
    payload: ReplaceExerciseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    week_start_date = workout_service.week_start_for_offset(payload.offset)
    plan = workout_service.get_plan_for_week(db, current_user, week_start_date)
    if plan is None:
        raise HTTPException(status_code=404, detail="No plan exists for that week")
    try:
        plan = workout_service.replace_exercise_in_plan(
            db, current_user, plan, payload.day_index, payload.exercise_index, payload.replacement_name
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return WorkoutWeekResponse(
        week_start_date=week_start_date,
        offset=payload.offset,
        is_before_registration=False,
        plan=WorkoutPlanResponse.model_validate(plan),
        plan_info=workout_service.build_plan_info(db, current_user, plan),
    )
