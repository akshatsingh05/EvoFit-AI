from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field


class DailyCheckInRequest(BaseModel):
    checkin_date: date
    workout_completed: bool
    workout_difficulty: int | None = Field(default=None, ge=1, le=5)
    sleep_hours: float = Field(ge=0, le=24)
    energy_level: int = Field(ge=1, le=5)
    water_intake_ml: int = Field(ge=0, le=10000)
    current_weight_kg: float | None = Field(default=None, gt=0, lt=400)
    mood: Literal["great", "good", "okay", "low", "bad"]
    muscle_soreness: int = Field(ge=1, le=5)
    pain_level: int = Field(ge=0, le=5)
    notes: str | None = Field(default=None, max_length=1000)


class DailyCheckInResponse(BaseModel):
    id: str
    checkin_date: date
    workout_completed: bool
    workout_difficulty: int | None
    sleep_hours: float
    energy_level: int
    water_intake_ml: int
    current_weight_kg: float | None
    mood: str
    muscle_soreness: int
    pain_level: int
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
