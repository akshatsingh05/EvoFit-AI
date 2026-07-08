import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    has_completed_onboarding: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    onboarding_profile = relationship(
        "OnboardingProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    medical_history = relationship(
        "MedicalHistory", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    settings = relationship(
        "UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    # No back_populates: RefreshToken doesn't need to navigate back to User
    # anywhere in the codebase (it's looked up by token_hash directly). The
    # DB-level ON DELETE CASCADE on RefreshToken.user_id already handles
    # cleanup on PostgreSQL (FK enforcement is on by default there); this
    # ORM-level cascade makes the same cleanup happen on SQLite too, where
    # FK actions aren't enforced by default (see database/session.py).
    refresh_tokens = relationship("RefreshToken", cascade="all, delete-orphan")
