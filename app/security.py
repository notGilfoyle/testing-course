"""
security.py — password hashing and JWT token logic.

This module is deliberately "pure": every function takes inputs and returns
outputs with no database or network calls. That makes it the ideal target for
UNIT TESTS (Phase 1) — each function can be tested in complete isolation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import (
    VerifyMismatchError,
    VerificationError,
    InvalidHashError,
)

# --- Config (normally these live in a settings file / env vars) ------------
SECRET_KEY = "dev-secret-not-for-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Argon2id hasher with library defaults (OWASP-recommended variant).
ph = PasswordHasher()


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
def hash_password(password: str) -> str:
    """Hash a plaintext password with Argon2id, returning the encoded hash."""
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its Argon2 hash.

    Returns False (never raises) on any mismatch or malformed hash, so callers
    always receive a boolean.
    """
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


# ---------------------------------------------------------------------------
# JWT access tokens
# ---------------------------------------------------------------------------
def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """
    Create a signed JWT for the given subject (e.g. a username or user id).

    The token carries:
      - 'sub' : the subject
      - 'exp' : expiry timestamp (now + expires_minutes)
    """
    minutes = expires_minutes if expires_minutes is not None else ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Decode and validate a JWT.

    Returns the 'sub' claim if the token is valid and unexpired.
    Returns None if the token is expired, tampered with, or otherwise invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
