from pydantic import BaseModel, EmailStr, Field


class ProfileUpdateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr | None = None


class ProfileResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    has_completed_onboarding: bool

    goals: dict | None = None
    body_metrics: dict | None = None
    fitness_experience: dict | None = None
    lifestyle_diet: dict | None = None

    medical_conditions: list[str] = []
    medical_injuries: list[str] = []
    medications: str | None = None
    allergies: str | None = None
    cleared_for_exercise: bool | None = None
