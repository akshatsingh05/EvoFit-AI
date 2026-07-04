from datetime import date, datetime
from pydantic import BaseModel


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


class WorkoutCompletionRequest(BaseModel):
    workout_date: date
    status: str  # "completed" | "skipped"


class WorkoutCompletionResponse(BaseModel):
    workout_date: date
    status: str

    model_config = {"from_attributes": True}
