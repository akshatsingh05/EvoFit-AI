from typing import Literal
from pydantic import BaseModel, Field


class WorkoutPreferencesResponse(BaseModel):
    workout_style: str | None = None
    workout_location: Literal["gym", "home", "mixed"] | None = None
    equipment_available: list[str] = []
    preferred_duration_minutes: int | None = None
    workout_intensity: Literal["light", "moderate", "high"] | None = None
    preferred_workout_time: Literal["morning", "afternoon", "evening"] | None = None
    favorite_muscle_groups: list[str] = []
    liked_exercises: list[str] = []
    disliked_exercises: list[str] = []
    avoid_movements: list[str] = []

    model_config = {"from_attributes": True}


class WorkoutPreferencesUpdateRequest(BaseModel):
    workout_style: str | None = None
    workout_location: Literal["gym", "home", "mixed"] | None = None
    equipment_available: list[str] | None = None
    preferred_duration_minutes: int | None = Field(default=None, ge=10, le=180)
    workout_intensity: Literal["light", "moderate", "high"] | None = None
    preferred_workout_time: Literal["morning", "afternoon", "evening"] | None = None
    favorite_muscle_groups: list[str] | None = None
    liked_exercises: list[str] | None = None
    disliked_exercises: list[str] | None = None
    avoid_movements: list[str] | None = None


class NutritionPreferencesResponse(BaseModel):
    diet_type: Literal["vegetarian", "vegan", "eggetarian", "non_vegetarian"] | None = None
    cuisine_preference: Literal["indian", "mediterranean", "asian", "western", "mixed"] | None = None
    budget: Literal["low", "medium", "high"] | None = None
    meals_per_day: int | None = None
    favorite_foods: list[str] = []
    disliked_foods: list[str] = []
    allergies: list[str] = []
    water_goal_ml: int | None = None
    preferred_snacks: list[str] = []
    cooking_time_preference: Literal["quick", "moderate", "anything"] | None = None

    model_config = {"from_attributes": True}


class NutritionPreferencesUpdateRequest(BaseModel):
    diet_type: Literal["vegetarian", "vegan", "eggetarian", "non_vegetarian"] | None = None
    cuisine_preference: Literal["indian", "mediterranean", "asian", "western", "mixed"] | None = None
    budget: Literal["low", "medium", "high"] | None = None
    meals_per_day: int | None = Field(default=None, ge=3, le=6)
    favorite_foods: list[str] | None = None
    disliked_foods: list[str] | None = None
    allergies: list[str] | None = None
    water_goal_ml: int | None = Field(default=None, ge=500, le=8000)
    preferred_snacks: list[str] | None = None
    cooking_time_preference: Literal["quick", "moderate", "anything"] | None = None
