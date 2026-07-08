"""
Password hashing and JWT token utilities.
Kept isolated from business logic so services stay thin and testable.
"""
import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

_PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).+$")

# bcrypt only uses the first 72 *bytes* of a password; anything beyond that
# is silently ignored by the algorithm itself, but the `bcrypt` library
# raises if you hand it more than 72 bytes rather than truncating for you.
# Truncate ourselves (on a UTF-8 boundary) so hashing never raises for a
# legitimately long-but-valid password (our schema already caps at 128
# characters, which can exceed 72 *bytes* once multi-byte characters are
# involved).
_BCRYPT_MAX_BYTES = 72


def _prepare_password_bytes(password: str) -> bytes:
    encoded = password.encode("utf-8")
    if len(encoded) <= _BCRYPT_MAX_BYTES:
        return encoded
    truncated = encoded[:_BCRYPT_MAX_BYTES]
    # Avoid splitting a multi-byte UTF-8 character in half.
    while truncated and (truncated[-1] & 0xC0) == 0x80:
        truncated = truncated[:-1]
    return truncated


def validate_password_complexity(password: str) -> str:
    """
    Shared by every schema that accepts a new password (signup, change
    password, and any future reset-password flow) so the rule can't drift
    out of sync between them the way it did when only signup enforced it.
    """
    if not _PASSWORD_PATTERN.match(password):
        raise ValueError("Password must contain at least one letter and one number")
    return password


def hash_password(password: str) -> str:
    # `bcrypt` (used directly, not through passlib -- see module docstring
    # note in git history / AUDIT_REPORT.md for why) returns bytes; store as
    # a plain str since that's what the `hashed_password` column expects.
    hashed = bcrypt.hashpw(_prepare_password_bytes(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare_password_bytes(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed/foreign hash format (e.g. a row seeded outside the app).
        # Treat as "does not match" rather than crashing the request.
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_minutes = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode: dict[str, Any] = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """Returns the subject (user id) encoded in the token, or None if invalid/expired/wrong type."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "access":
            return None
        subject = payload.get("sub")
        return str(subject) if subject is not None else None
    except JWTError:
        return None


# --- Refresh tokens -----------------------------------------------------
#
# Refresh tokens are opaque, high-entropy random strings (not JWTs) so that
# revoking one is a simple DB lookup rather than requiring a JWT blacklist.
# Only a SHA-256 hash of the token is ever persisted, so a leaked database
# does not expose usable tokens.

def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def refresh_token_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
