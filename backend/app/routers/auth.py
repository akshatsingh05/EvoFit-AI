from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.rate_limit import limiter
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    AccessTokenResponse,
    RefreshRequest,
    LogoutRequest,
    UserResponse,
    ForgotPasswordRequest,
    MessageResponse,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Shared OpenAPI examples ------------------------------------------------
_TOKEN_RESPONSE_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "6yA1n8s2q9c...",
    "token_type": "bearer",
    "user": {
        "id": "6f9c1e2a-...",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "has_completed_onboarding": False,
    },
}


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=201,
    summary="Create a new account",
    description=(
        "Creates a user account and immediately signs them in, returning an "
        "access token (15 min default expiry) and a refresh token (30 day "
        "default expiry, see REFRESH_TOKEN_EXPIRE_DAYS). Password must be "
        "8-128 characters and contain at least one letter and one digit. "
        "Rate limited (see AUTH_RATE_LIMIT) to slow down automated signup abuse."
    ),
    responses={
        201: {"content": {"application/json": {"example": _TOKEN_RESPONSE_EXAMPLE}}},
        409: {"description": "An account with this email already exists"},
        422: {"description": "Validation failed (e.g. password too weak)"},
        429: {"description": "Too many requests"},
    },
)
@limiter.limit(settings.AUTH_RATE_LIMIT)
def signup(request: Request, payload: SignupRequest, db: Session = Depends(get_db)):
    access_token, refresh_token, user = auth_service.signup(db, payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
    description="Exchanges valid credentials for a fresh access/refresh token pair. Rate limited.",
    responses={
        200: {"content": {"application/json": {"example": _TOKEN_RESPONSE_EXAMPLE}}},
        401: {"description": "Incorrect email or password"},
        429: {"description": "Too many requests"},
    },
)
@limiter.limit(settings.AUTH_RATE_LIMIT)
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    access_token, refresh_token, user = auth_service.login(db, payload)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Exchange a refresh token for a new access token",
    description=(
        "Refresh tokens are single-use: this call revokes the supplied token "
        "and returns a new access/refresh pair (rotation). Reusing an already-"
        "rotated, revoked, or expired refresh token returns 401 -- the "
        "frontend's axios interceptor treats that as 'session expired' and "
        "redirects to /login."
    ),
    responses={401: {"description": "Invalid, expired, or already-used refresh token"}},
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    access_token, refresh_token = auth_service.refresh_access_token(db, payload.refresh_token)
    return AccessTokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out and revoke a refresh token",
    description=(
        "Revokes the given refresh token server-side so it can no longer be "
        "used to mint new access tokens, even before its natural expiry. "
        "Idempotent: logging out twice with the same token is not an error."
    ),
)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    auth_service.logout(db, payload.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password reset",
    description=(
        "Always returns the same generic message whether or not the email "
        "belongs to an account, to avoid leaking which emails are registered."
    ),
)
@limiter.limit(settings.AUTH_RATE_LIMIT)
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    auth_service.request_password_reset(db, payload.email)
    return MessageResponse(message="If an account exists for that email, a reset link has been sent.")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current authenticated user",
    description="Requires a valid, non-expired access token in the Authorization: Bearer header.",
    responses={401: {"description": "Missing, invalid, or expired access token"}},
)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
