from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.daily_checkin import DailyCheckIn
from app.models.progress import WeightLog
from app.schemas.daily_checkin import DailyCheckInRequest
from app.services import notification_service


def _log_weight_from_checkin(db: Session, user: User, log_date: date, weight_kg: float) -> None:
    """
    Direct WeightLog upsert (rather than calling progress_service.log_weight)
    to avoid a circular import — progress_service depends on this module for
    check-in history.
    """
    existing = db.query(WeightLog).filter(WeightLog.user_id == user.id, WeightLog.log_date == log_date).first()
    if existing:
        existing.weight_kg = weight_kg
    else:
        db.add(WeightLog(user_id=user.id, log_date=log_date, weight_kg=weight_kg))
    db.commit()


def upsert_checkin(db: Session, user: User, payload: DailyCheckInRequest) -> DailyCheckIn:
    existing = (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date == payload.checkin_date)
        .first()
    )

    fields = payload.model_dump()
    if existing:
        for key, value in fields.items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        record = existing
    else:
        record = DailyCheckIn(user_id=user.id, **fields)
        db.add(record)
        db.commit()
        db.refresh(record)

    if payload.current_weight_kg:
        _log_weight_from_checkin(db, user, payload.checkin_date, payload.current_weight_kg)

    notification_service.create_notification(
        db, user, "profile_updated", f"Check-in saved for {payload.checkin_date.strftime('%A, %b %-d')}."
    )

    return record


def get_checkin_for_date(db: Session, user: User, checkin_date: date) -> DailyCheckIn | None:
    return (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date == checkin_date)
        .first()
    )


def has_checked_in_today(db: Session, user: User) -> bool:
    return get_checkin_for_date(db, user, date.today()) is not None


def get_recent_checkins(db: Session, user: User, days: int = 7) -> list[DailyCheckIn]:
    cutoff = date.today() - timedelta(days=days)
    return (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id, DailyCheckIn.checkin_date >= cutoff)
        .order_by(DailyCheckIn.checkin_date.asc())
        .all()
    )


def get_history(db: Session, user: User, limit: int = 60) -> list[DailyCheckIn]:
    return (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id)
        .order_by(DailyCheckIn.checkin_date.desc())
        .limit(limit)
        .all()
    )
