from datetime import date, datetime
from pydantic import BaseModel


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


class MealCompletionRequest(BaseModel):
    meal_date: date
    meal_type: str
    status: str  # "completed" | "skipped"


class MealCompletionResponse(BaseModel):
    meal_date: date
    meal_type: str
    status: str

    model_config = {"from_attributes": True}
