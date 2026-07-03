from pydantic import BaseModel


class MedicalHistoryRequest(BaseModel):
    conditions: list[str] = []
    injuries: list[str] = []
    medications: str | None = None
    allergies: str | None = None
    additional_notes: str | None = None
    cleared_for_exercise: bool = True


class MedicalHistoryResponse(BaseModel):
    conditions: list[str] = []
    injuries: list[str] = []
    medications: str | None = None
    allergies: str | None = None
    additional_notes: str | None = None
    cleared_for_exercise: bool

    model_config = {"from_attributes": True}
