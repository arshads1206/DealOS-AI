"""
DealOS AI — Authentication Service.

Orchestrates the authentication flow: registration, login, token refresh.

This is the SERVICE layer — it coordinates between:
- Repository (data access)
- Security module (password hashing, JWT)
- Audit log (compliance tracking)

The service layer is where business rules live:
- "Email must be unique" → checked here, not in the repository
- "Password must be hashed before storage" → enforced here
- "Login must be audited" → triggered here
- "Refresh tokens generate new access tokens" → logic here

Why not put this in the endpoint handler?
- Endpoints handle HTTP concerns (request parsing, response formatting)
- Services handle business logic (validation, orchestration, rules)
- This separation enables reuse (CLI, background jobs can call the service)
"""

import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.permissions import get_permissions
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_refresh_token,
)
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserProfile, UserResponse

logger = structlog.get_logger(__name__)


class AuthService:
    """Authentication business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._audit_repo = AuditLogRepository(session)

    async def register(
        self,
        data: RegisterRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> UserResponse:
        """
        Register a new user.

        Flow:
        1. Check email uniqueness
        2. Hash password
        3. Create user with default ANALYST role
        4. Log registration in audit trail
        5. Return user response (no password hash)

        New users default to ANALYST role — the most common role.
        Admin promotion requires an existing admin.
        """
        # Check email uniqueness
        if await self._user_repo.email_exists(data.email):
            raise ConflictError(
                message=f"Email '{data.email}' is already registered",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        # Hash password before storage
        hashed = hash_password(data.password)

        # Create user
        user = await self._user_repo.create(
            email=data.email,
            hashed_password=hashed,
            full_name=data.full_name,
            role=UserRole.ANALYST,
            status="active",
        )

        # Audit log
        await self._audit_repo.create(
            action="user.register",
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            new_values={"email": data.email, "role": UserRole.ANALYST},
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info("user_registered", user_id=str(user.id), email=data.email)

        return UserResponse.model_validate(user)

    async def login(
        self,
        data: LoginRequest,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        """
        Authenticate a user and return JWT token pair.

        Flow:
        1. Find user by email
        2. Verify password
        3. Check user is active
        4. Generate access + refresh tokens
        5. Update last_login_at
        6. Log login in audit trail

        Security: Uses the same error message for "user not found" and
        "wrong password" to prevent user enumeration attacks.
        """
        # Find user
        user = await self._user_repo.get_by_email(data.email)

        if user is None:
            # Generic message prevents user enumeration
            raise AuthenticationError(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        # Verify password
        if not verify_password(data.password, user.hashed_password):
            logger.warning("login_failed_bad_password", email=data.email)
            raise AuthenticationError(
                message="Invalid email or password",
                error_code="INVALID_CREDENTIALS",
            )

        # Check account status
        if user.status != "active":
            raise AuthenticationError(
                message="Account is deactivated",
                error_code="ACCOUNT_INACTIVE",
            )

        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )
        refresh_token = create_refresh_token(user_id=str(user.id))

        # Update last login
        await self._user_repo.update_last_login(user.id)

        # Audit log
        await self._audit_repo.create(
            action="user.login",
            user_id=user.id,
            resource_type="user",
            resource_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        logger.info("user_logged_in", user_id=str(user.id), email=user.email)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate a new access token using a valid refresh token.

        Flow:
        1. Decode and verify refresh token
        2. Look up user (ensure still active)
        3. Generate new access token
        4. Return new token pair (rotate refresh token for security)

        Refresh token rotation: Each refresh generates a NEW refresh token,
        invalidating the old one. This limits the window of exposure if a
        refresh token is compromised.
        """
        # Verify refresh token
        payload = verify_refresh_token(refresh_token)
        user_id = payload["sub"]

        # Look up user
        user = await self._user_repo.get_by_id(uuid.UUID(user_id))

        if user is None or user.status != "active":
            raise AuthenticationError(
                message="User not found or inactive",
                error_code="USER_INACTIVE",
            )

        # Generate new token pair
        new_access_token = create_access_token(
            user_id=str(user.id),
            email=user.email,
            role=user.role,
        )
        new_refresh_token = create_refresh_token(user_id=str(user.id))

        logger.info("token_refreshed", user_id=str(user.id))

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def get_current_user_profile(self, user_id: str) -> UserProfile:
        """
        Get the current user's profile with permissions.

        Used by the /me endpoint — returns the user's data plus their
        computed permission set for frontend RBAC.
        """
        user = await self._user_repo.get_by_id(uuid.UUID(user_id))

        if user is None:
            raise AuthenticationError(
                message="User not found",
                error_code="USER_NOT_FOUND",
            )

        permissions = list(get_permissions(user.role))

        return UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            permissions=permissions,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
        )
