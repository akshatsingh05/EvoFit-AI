from datetime import datetime
from pydantic import BaseModel


class AdaptiveInsightResponse(BaseModel):
    id: str
    recovery_score: int
    consistency_pct: int
    fatigue_flag: bool
    intensity_modifier: int
    nutrition_calorie_adjustment: float
    recommendations: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
