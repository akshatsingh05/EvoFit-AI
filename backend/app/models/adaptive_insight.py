import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class AdaptiveInsight(Base):
    """
    One row per adaptive-analysis run. Kept as history (not overwritten) so
    Progress can show how recovery/recommendations evolved over time.
    """

    __tablename__ = "adaptive_insights"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)

    recovery_score: Mapped[int] = mapped_column(Integer, nullable=False)
    consistency_pct: Mapped[int] = mapped_column(Integer, nullable=False)
    fatigue_flag: Mapped[bool] = mapped_column(nullable=False)
    intensity_modifier: Mapped[int] = mapped_column(Integer, nullable=False)  # -1, 0, or +1
    nutrition_calorie_adjustment: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    recommendations: Mapped[list] = mapped_column(JSON, nullable=False)  # list[str]
    analysis_basis: Mapped[dict] = mapped_column(JSON, nullable=False)  # snapshot of inputs, for transparency
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
