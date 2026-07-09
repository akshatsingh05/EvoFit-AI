import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class ImportedPlan(Base):
    """
    A user-uploaded workout or nutrition plan (Sprint 5). `raw_text` is the
    extracted text (from manual input, TXT, PDF, DOCX, or OCR on an image).
    `parsed_data` is the normalized structure produced by the plan parser
    (see app/services/workout_plan_parser.py / nutrition_plan_parser.py).
    Every import is kept (never overwritten) so Plan History (Feature 7) can
    list and reopen past imports.
    """

    __table_args__ = (Index("ix_imported_plans_user_type", "user_id", "plan_type"),)

    __tablename__ = "imported_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    plan_type: Mapped[str] = mapped_column(String, nullable=False)  # "workout" | "nutrition"
    plan_name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)  # manual|txt|pdf|docx|image
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    applied_status: Mapped[str] = mapped_column(String, nullable=False, default="none")  # none|used_mine|merged|used_evofit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")


class PlanAnalysis(Base):
    """
    The result of comparing one ImportedPlan against the user's current
    EvoFit AI plan (Feature 3/4/5). Stored so Plan History can show the
    comparison report and AI analysis without recomputing it, and so exports
    (Feature 8) can be regenerated on demand from a stable snapshot.
    """

    __tablename__ = "plan_analyses"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    imported_plan_id: Mapped[str] = mapped_column(String, ForeignKey("imported_plans.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    comparison: Mapped[dict] = mapped_column(JSON, nullable=False)
    observations: Mapped[list] = mapped_column(JSON, nullable=False)
    suggestions: Mapped[list] = mapped_column(JSON, nullable=False)
    effectiveness_score: Mapped[dict] = mapped_column(JSON, nullable=False)  # {mine: int, evofit: int}
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User")
    imported_plan = relationship("ImportedPlan")
