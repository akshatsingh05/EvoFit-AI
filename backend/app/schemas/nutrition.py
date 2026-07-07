from datetime import date, datetime
from pydantic import BaseModel

from app.schemas.plan_info import PlanInfoSchema
from app.schemas.history import HistoryListResponse  # noqa: F401 (re-exported for router convenience)


class MealSchema(BaseModel):
    meal_type: str
    name: str
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int


class NutritionPlanResponse(BaseModel):
    id: str
    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int
    water_goal_ml: int
    meals: list[MealSchema]
    created_at: datetime

    model_config = {"from_attributes": True}


class NutritionDaySchema(BaseModel):
    day_name: str
    date: date
    target_calories: int
    target_protein_g: int
    target_carbs_g: int
    target_fat_g: int
    water_goal_ml: int
    meals: list[MealSchema]


class NutritionWeekPlanResponse(BaseModel):
    id: str
    week_start_date: date
    days: list[NutritionDaySchema]
    created_at: datetime

    model_config = {"from_attributes": True}


class NutritionWeekResponse(BaseModel):
    """Response for week-navigation requests. `plan` is null for weeks before
    the user registered, mirroring WorkoutWeekResponse."""

    week_start_date: date
    offset: int
    is_before_registration: bool
    plan: NutritionWeekPlanResponse | None = None
    plan_info: PlanInfoSchema | None = None


class MealCompletionRequest(BaseModel):
    meal_date: date
    meal_type: str
    status: str  # "completed" | "skipped"


class MealCompletionResponse(BaseModel):
    meal_date: date
    meal_type: str
    status: str

    model_config = {"from_attributes": True}
