import uuid
from datetime import datetime, date, timezone

from sqlalchemy import String, DateTime, Date, ForeignKey, Float, Integer, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class DailyCheckIn(Base):
    """One check-in per user per day. Re-submitting the same date updates it (idempotent)."""

    __tablename__ = "daily_checkins"
    __table_args__ = (UniqueConstraint("user_id", "checkin_date", name="uq_checkin_user_date"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    checkin_date: Mapped[date] = mapped_column(Date, nullable=False)

    workout_completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    workout_difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1 (easy) - 5 (max effort)
    sleep_hours: Mapped[float] = mapped_column(Float, nullable=False)
    energy_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    water_intake_ml: Mapped[int] = mapped_column(Integer, nullable=False)
    current_weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    mood: Mapped[str] = mapped_column(String, nullable=False)  # great|good|okay|low|bad
    muscle_soreness: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-5
    pain_level: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-5
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
