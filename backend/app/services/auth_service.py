import logging

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest

logger = logging.getLogger("evofit.auth")


def signup(db: Session, payload: SignupRequest) -> tuple[str, User]:
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

    token = create_access_token(subject=user.id)
    return token, user


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


def login(db: Session, payload: LoginRequest) -> tuple[str, User]:
    invalid_creds = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
    )
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise invalid_creds

    token = create_access_token(subject=user.id)
    return token, user
