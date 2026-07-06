"""
DealOS AI — Authentication Endpoints.

REST API for user authentication:
- POST /register — Create a new account
- POST /login — Authenticate and receive JWT tokens
- POST /logout — Invalidate session (client-side token discard)
- POST /refresh — Get a new access token using refresh token
- GET /me — Get current user profile with permissions

Endpoint design follows REST conventions:
- POST for state-changing operations
- GET for idempotent reads
- Consistent error responses via the global error handler
- Request/response validation via Pydantic schemas
"""

from fastapi import APIRouter, Request

from app.dependencies import DbSession
from app.api.middleware.auth import CurrentUser
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import UserProfile, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user account",
    responses={
        201: {"description": "User created successfully"},
        409: {"description": "Email already registered"},
        422: {"description": "Validation error (weak password, etc.)"},
    },
)
async def register(
    data: RegisterRequest,
    request: Request,
    db: DbSession,
):
    """
    Register a new user account.

    New users are assigned the **Analyst** role by default.
    Admin role assignment requires an existing admin.

    Password requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    service = AuthService(db)
    return await service.register(
        data=data,
        ip_address=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
    responses={
        200: {"description": "Login successful, tokens returned"},
        401: {"description": "Invalid credentials"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def login(
    data: LoginRequest,
    request: Request,
    db: DbSession,
):
    """
    Authenticate with email and password.

    Returns a JWT access token (15 min) and refresh token (7 days).
    Use the access token in the `Authorization: Bearer <token>` header.
    """
    service = AuthService(db)
    return await service.login(
        data=data,
        ip_address=_get_client_ip(request),
        user_agent=request.headers.get("user-agent"),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout (client-side token discard)",
    responses={
        200: {"description": "Logout successful"},
    },
)
async def logout(current_user: CurrentUser):
    """
    Logout the current user.

    Since JWTs are stateless, logout is handled client-side by discarding
    the tokens. This endpoint exists for:
    1. API completeness
    2. Future server-side token blacklisting (Redis-backed)
    3. Audit trail (the auth middleware logs this action)

    In a production system, the refresh token would be added to a Redis
    blacklist to prevent reuse.
    """
    return MessageResponse(message="Logged out successfully")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    responses={
        200: {"description": "New token pair returned"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: DbSession,
):
    """
    Get a new access token using a valid refresh token.

    Implements refresh token rotation — each refresh generates a new
    refresh token, invalidating the previous one.
    """
    service = AuthService(db)
    return await service.refresh_access_token(data.refresh_token)


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile",
    responses={
        200: {"description": "User profile with permissions"},
        401: {"description": "Not authenticated"},
    },
)
async def get_me(
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get the current authenticated user's profile.

    Returns the user's data plus their computed permission set,
    which the frontend uses for client-side RBAC (showing/hiding
    UI elements based on role).
    """
    service = AuthService(db)
    return await service.get_current_user_profile(current_user["user_id"])


# ── Helper ──


def _get_client_ip(request: Request) -> str:
    """Extract client IP from request headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
