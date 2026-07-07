import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_refresh_token,
    hash_refresh_token,
    refresh_token_expiry,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import SignupRequest, LoginRequest

logger = logging.getLogger("evofit.auth")


def _issue_tokens(db: Session, user: User) -> tuple[str, str]:
    """Creates a new access token plus a new server-tracked refresh token."""
    access_token = create_access_token(subject=user.id)

    raw_refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()

    return access_token, raw_refresh_token


def signup(db: Session, payload: SignupRequest) -> tuple[str, str, User]:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, refresh_token = _issue_tokens(db, user)
    return access_token, refresh_token, user


def request_password_reset(db: Session, email: str) -> None:
    """
    Issues a short-lived reset token if the account exists.
    Always behaves identically to the caller regardless of whether the
    email matches an account, to avoid leaking which emails are registered.
    In production this token would be emailed via a transactional email
    provider rather than logged.
    """
    user = db.query(User).filter(User.email == email.lower()).first()
    if user:
        reset_token = create_access_token(subject=f"reset:{user.id}", expires_minutes=30)
        logger.info("Password reset requested for user_id=%s token=%s", user.id, reset_token)


def login(db: Session, payload: LoginRequest) -> tuple[str, str, User]:
    invalid_creds = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise invalid_creds

    access_token, refresh_token = _issue_tokens(db, user)
    return access_token, refresh_token, user


def refresh_access_token(db: Session, raw_refresh_token: str) -> tuple[str, str]:
    """
    Validates a refresh token and rotates it: the old one is revoked and a
    new access + refresh token pair is issued. Rotation limits the damage if
    a refresh token is ever intercepted, since it becomes single-use.
    """
    invalid = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    token_hash = hash_refresh_token(raw_refresh_token)
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    if record is None or record.revoked:
        raise invalid

    from datetime import datetime, timezone

    if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise invalid

    user = db.get(User, record.user_id)
    if user is None:
        raise invalid

    record.revoked = True
    db.add(record)
    db.commit()

    access_token, new_refresh_token = _issue_tokens(db, user)
    return access_token, new_refresh_token


def logout(db: Session, raw_refresh_token: str) -> None:
    """Revokes a refresh token so it can no longer be used to mint access tokens."""
    token_hash = hash_refresh_token(raw_refresh_token)
    record = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if record is not None and not record.revoked:
        record.revoked = True
        db.add(record)
        db.commit()
