"""
DealOS AI — JWT Authentication Middleware.

Provides FastAPI dependencies for extracting and validating JWT tokens
from request headers, and resolving the current user.

Design decisions:
1. Bearer token in Authorization header (RFC 6750): Industry standard.
2. Returns a dict, not a User ORM object: Avoids a DB query on every request.
   The JWT payload contains user_id, email, and role — sufficient for most
   authorization decisions. Full user object is fetched only when needed.
3. Optional auth dependency: Some endpoints (health, docs) don't require auth.
"""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationError
from app.core.security import verify_access_token

# HTTPBearer extracts the token from the "Authorization: Bearer <token>" header.
# auto_error=False allows us to handle missing tokens ourselves for better error messages.
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict:
    """
    Extract and validate JWT from the Authorization header.

    Returns a dict with user claims:
        {
            "user_id": "uuid-string",
            "email": "user@example.com",
            "role": "analyst",
        }

    This dependency is injected into any endpoint that requires authentication.

    Usage:
        @router.get("/protected")
        async def protected_endpoint(current_user: CurrentUser):
            user_id = current_user["user_id"]
            ...
    """
    if credentials is None:
        raise AuthenticationError(
            message="Authentication required",
            error_code="AUTH_REQUIRED",
            details={"hint": "Include 'Authorization: Bearer <token>' header"},
        )

    token = credentials.credentials

    # Verify and decode the access token
    payload = verify_access_token(token)

    return {
        "user_id": payload["sub"],
        "email": payload.get("email", ""),
        "role": payload.get("role", ""),
    }


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> dict | None:
    """
    Optionally extract user from JWT.

    Returns None if no token is provided (for endpoints that work
    with or without authentication, like public search).
    """
    if credentials is None:
        return None

    try:
        payload = verify_access_token(credentials.credentials)
        return {
            "user_id": payload["sub"],
            "email": payload.get("email", ""),
            "role": payload.get("role", ""),
        }
    except AuthenticationError:
        return None


# ── Type Aliases ──
# Clean endpoint signatures: `current_user: CurrentUser` instead of
# `current_user: dict = Depends(get_current_user)`

CurrentUser = Annotated[dict, Depends(get_current_user)]
OptionalUser = Annotated[dict | None, Depends(get_optional_user)]
