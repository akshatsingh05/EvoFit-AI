from typing import Literal
from pydantic import BaseModel, Field


class SettingsResponse(BaseModel):
    theme: Literal["light", "dark"]
    email_notifications: bool
    push_notifications: bool
    weekly_summary_email: bool

    model_config = {"from_attributes": True}


class SettingsUpdateRequest(BaseModel):
    theme: Literal["light", "dark"] | None = None
    email_notifications: bool | None = None
    push_notifications: bool | None = None
    weekly_summary_email: bool | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str
