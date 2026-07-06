"""
DealOS AI — Security Utilities.

Handles JWT token lifecycle and password hashing.

Design decisions:
1. Access + Refresh token pair: Access tokens are short-lived (15 min) to limit
   damage if stolen. Refresh tokens are long-lived (7 days) for user convenience.
   This is the industry standard for financial platforms (Bloomberg, Refinitiv).

2. bcrypt for password hashing: Adaptive cost factor makes brute-force attacks
   computationally expensive. OWASP-recommended. passlib provides a clean API
   with automatic salt generation.

3. Token payload includes role: Avoids a database lookup on every request.
   Role changes require re-authentication (acceptable tradeoff for performance).

4. Token type field ("access" vs "refresh"): Prevents refresh tokens from being
   used as access tokens — a common vulnerability in naive JWT implementations.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.core.exceptions import AuthenticationError

# ── Password Hashing ──
# bcrypt with automatic salt generation.
# `deprecated="auto"` ensures old hashes are re-hashed on verification
# if the algorithm or cost factor changes.

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Returns a string like: $2b$12$...
    The salt is embedded in the hash — no separate storage needed.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Uses constant-time comparison to prevent timing attacks.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ──


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    Payload:
        sub: User ID (standard JWT claim)
        email: User email for display
        role: User role for RBAC checks
        type: "access" (prevents refresh token misuse)
        exp: Expiration timestamp
        iat: Issued-at timestamp
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "exp": now + expires_delta,
        "iat": now,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    user_id: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a long-lived JWT refresh token.

    Refresh tokens contain minimal claims — only user ID and type.
    They are used exclusively to obtain new access tokens.
    """
    settings = get_settings()
    now = datetime.now(timezone.utc)

    if expires_delta is None:
        expires_delta = timedelta(days=settings.jwt_refresh_token_expire_days)

    payload: dict[str, Any] = {
        "sub": user_id,
        "type": "refresh",
        "exp": now + expires_delta,
        "iat": now,
    }

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Raises AuthenticationError if:
    - Token is expired
    - Token signature is invalid
    - Token is malformed
    """
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(
            message="Token has expired",
            error_code="TOKEN_EXPIRED",
        )
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(
            message="Invalid token",
            error_code="TOKEN_INVALID",
            details={"reason": str(e)},
        )


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Decode a token and verify it is an access token (not refresh).

    This prevents the common vulnerability where refresh tokens
    are accepted in place of access tokens.
    """
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise AuthenticationError(
            message="Invalid token type",
            error_code="INVALID_TOKEN_TYPE",
            details={"expected": "access", "got": payload.get("type")},
        )

    return payload


def verify_refresh_token(token: str) -> dict[str, Any]:
    """
    Decode a token and verify it is a refresh token.

    Returns the payload with the user_id for access token regeneration.
    """
    payload = decode_token(token)

    if payload.get("type") != "refresh":
        raise AuthenticationError(
            message="Invalid token type",
            error_code="INVALID_TOKEN_TYPE",
            details={"expected": "refresh", "got": payload.get("type")},
        )

    return payload
