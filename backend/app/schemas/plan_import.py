from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ManualImportRequest(BaseModel):
    plan_name: str = Field(min_length=1, max_length=120)
    raw_text: str = Field(min_length=1)


class ImportedPlanResponse(BaseModel):
    id: str
    plan_type: str
    plan_name: str
    source_type: str
    raw_text: str
    parsed_data: dict[str, Any]
    applied_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportedPlanSummary(BaseModel):
    """Lighter shape for history lists -- omits raw_text/parsed_data."""
    id: str
    plan_type: str
    plan_name: str
    source_type: str
    applied_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ImportHistoryResponse(BaseModel):
    entries: list[ImportedPlanSummary]


class PlanAnalysisResponse(BaseModel):
    id: str
    imported_plan_id: str
    comparison: dict[str, Any]
    observations: list[str]
    suggestions: list[dict[str, Any]]
    effectiveness_score: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


class ApplyDecisionRequest(BaseModel):
    mode: Literal["use_mine", "merge", "use_evofit"]


class ApplyDecisionResponse(BaseModel):
    mode: str
    plan_type: str
    workout_plan_id: str | None = None
    nutrition_plan_id: str | None = None
