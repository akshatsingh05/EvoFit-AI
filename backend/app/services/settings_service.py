from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import verify_password, hash_password
from app.models.user import User
from app.models.user_settings import UserSettings
from app.models.refresh_token import RefreshToken
from app.schemas.settings import SettingsUpdateRequest, ChangePasswordRequest


def _get_or_create_settings(db: Session, user: User) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if settings is None:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def get_settings(db: Session, user: User) -> UserSettings:
    return _get_or_create_settings(db, user)


def update_settings(db: Session, user: User, payload: SettingsUpdateRequest) -> UserSettings:
    settings = _get_or_create_settings(db, user)

    if payload.theme is not None:
        settings.theme = payload.theme
    if payload.email_notifications is not None:
        settings.email_notifications = payload.email_notifications
    if payload.push_notifications is not None:
        settings.push_notifications = payload.push_notifications
    if payload.weekly_summary_email is not None:
        settings.weekly_summary_email = payload.weekly_summary_email

    db.commit()
    db.refresh(settings)
    return settings


def change_password(db: Session, user: User, payload: ChangePasswordRequest) -> None:
    if not verify_password(payload.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Current password is incorrect")

    user.hashed_password = hash_password(payload.new_password)

    # A stolen refresh token must stop working the moment the legitimate
    # user changes their password -- otherwise an attacker holding one keeps
    # minting fresh access tokens indefinitely regardless of the password
    # change. This revokes every session; the user (and anyone else with a
    # copy of a refresh token) will need to log in again everywhere.
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id, RefreshToken.revoked.is_(False)
    ).update({"revoked": True})

    db.commit()
