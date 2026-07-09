from datetime import date, datetime
from pydantic import BaseModel, Field

from app.schemas.plan_info import PlanInfoSchema
from app.schemas.history import HistoryListResponse  # noqa: F401 (re-exported for router convenience)


class ExerciseSchema(BaseModel):
    name: str
    sets: int
    reps: str
    rest_seconds: int
    instructions: str


class WorkoutDaySchema(BaseModel):
    day_name: str
    is_rest_day: bool
    focus: str
    exercises: list[ExerciseSchema]
    estimated_duration_minutes: int


class WorkoutPlanResponse(BaseModel):
    id: str
    week_start_date: date
    schedule: list[WorkoutDaySchema]
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkoutWeekResponse(BaseModel):
    """Response for week-navigation requests. `plan` is null for weeks before
    the user registered, or in-between weeks the app is not allowed to generate."""

    week_start_date: date
    offset: int
    is_before_registration: bool
    plan: WorkoutPlanResponse | None = None
    plan_info: PlanInfoSchema | None = None


class CalendarWorkoutDetail(BaseModel):
    focus: str | None = None
    exercises: list[dict] = []
    duration_minutes: int = 0
    completion_status: str | None = None


class CalendarDayResponse(BaseModel):
    date: date
    status: str  # completed | skipped | rest | upcoming | missed | no_plan
    workout: CalendarWorkoutDetail | None = None


class WorkoutCalendarResponse(BaseModel):
    start_date: date
    end_date: date
    days: list[CalendarDayResponse]
    streak: int


class WorkoutCompletionRequest(BaseModel):
    workout_date: date
    status: str  # "completed" | "skipped"


class WorkoutCompletionResponse(BaseModel):
    workout_date: date
    status: str

    model_config = {"from_attributes": True}


class ExerciseAlternativesResponse(BaseModel):
    alternatives: list[str]


class ReplaceExerciseRequest(BaseModel):
    offset: int = 0
    day_index: int = Field(ge=0, le=6)
    exercise_index: int = Field(ge=0)
    replacement_name: str | None = None  # None = auto "Swap"
