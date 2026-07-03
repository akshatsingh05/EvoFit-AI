import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class MedicalHistory(Base):
    __tablename__ = "medical_history"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), unique=True, nullable=False)

    conditions: Mapped[list | None] = mapped_column(JSON, nullable=True)  # e.g. ["asthma", "diabetes_type_2"]
    injuries: Mapped[list | None] = mapped_column(JSON, nullable=True)  # e.g. ["lower_back", "left_knee"]
    medications: Mapped[str | None] = mapped_column(Text, nullable=True)
    allergies: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cleared_for_exercise: Mapped[bool] = mapped_column(default=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user = relationship("User", back_populates="medical_history")
