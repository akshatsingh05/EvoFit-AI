from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User

VALID_TYPES = {"workout_reminder", "meal_reminder", "workout_completed", "goal_achieved", "profile_updated"}


def create_notification(db: Session, user: User, notif_type: str, message: str) -> Notification:
    if notif_type not in VALID_TYPES:
        raise ValueError(f"Unknown notification type: {notif_type}")
    notification = Notification(user_id=user.id, type=notif_type, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def list_notifications(db: Session, user: User, limit: int = 50) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )


def unread_count(db: Session, user: User) -> int:
    return db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).count()


def mark_read(db: Session, user: User, notification_id: str) -> Notification | None:
    notification = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user.id)
        .first()
    )
    if notification is None:
        return None
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, user: User) -> None:
    db.query(Notification).filter(Notification.user_id == user.id, Notification.is_read.is_(False)).update(
        {"is_read": True}
    )
    db.commit()
