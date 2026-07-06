"""
DealOS AI — User Management Service.

Admin-level user management: create, list, update, deactivate users.

Separation from AuthService:
- AuthService handles self-service operations (register, login, refresh)
- UserService handles admin operations (CRUD, role changes, account status)

This mirrors how enterprise identity platforms work (Okta, Azure AD):
users self-register, but admins manage roles and account lifecycle.
"""

import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import hash_password
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate

logger = structlog.get_logger(__name__)


class UserService:
    """User management business logic (admin operations)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._audit_repo = AuditLogRepository(session)

    async def create_user(
        self,
        data: UserCreate,
        created_by: uuid.UUID,
        ip_address: str | None = None,
    ) -> UserResponse:
        """
        Create a new user (admin-only).

        Unlike registration, admin creation allows setting any role.
        Used for provisioning analyst accounts in bulk.
        """
        # Check email uniqueness
        if await self._user_repo.email_exists(data.email):
            raise ConflictError(
                message=f"Email '{data.email}' is already registered",
                error_code="EMAIL_ALREADY_EXISTS",
            )

        # Validate role
        valid_roles = {r.value for r in UserRole}
        if data.role not in valid_roles:
            raise ValidationError(
                message=f"Invalid role: {data.role}",
                error_code="INVALID_ROLE",
                details={"valid_roles": list(valid_roles)},
            )

        # Create user
        user = await self._user_repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role,
            status="active",
        )

        # Audit
        await self._audit_repo.create(
            action="user.create",
            user_id=created_by,
            resource_type="user",
            resource_id=user.id,
            new_values={"email": data.email, "role": data.role},
            ip_address=ip_address,
        )

        logger.info(
            "user_created_by_admin",
            user_id=str(user.id),
            created_by=str(created_by),
        )

        return UserResponse.model_validate(user)

    async def get_user(self, user_id: uuid.UUID) -> UserResponse:
        """Get a single user by ID."""
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(resource="User", resource_id=str(user_id))
        return UserResponse.model_validate(user)

    async def list_users(
        self, skip: int = 0, limit: int = 20
    ) -> tuple[list[UserResponse], int]:
        """
        List all users with pagination.

        Returns (users, total_count) for pagination metadata.
        """
        users = await self._user_repo.get_all(skip=skip, limit=limit)
        total = await self._user_repo.count()
        return [UserResponse.model_validate(u) for u in users], total

    async def update_user(
        self,
        user_id: uuid.UUID,
        data: UserUpdate,
        updated_by: uuid.UUID,
        ip_address: str | None = None,
    ) -> UserResponse:
        """
        Update a user's profile or role.

        Role changes are sensitive operations — they're always audited
        with old and new values for compliance.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(resource="User", resource_id=str(user_id))

        # Build update dict from non-None fields
        update_data = data.model_dump(exclude_none=True)

        if not update_data:
            return UserResponse.model_validate(user)

        # Validate role if being changed
        if "role" in update_data:
            valid_roles = {r.value for r in UserRole}
            if update_data["role"] not in valid_roles:
                raise ValidationError(
                    message=f"Invalid role: {update_data['role']}",
                    error_code="INVALID_ROLE",
                )

        # Track old values for audit
        old_values = {
            k: getattr(user, k)
            for k in update_data
            if hasattr(user, k)
        }

        # Check email uniqueness if changing
        if "email" in update_data and update_data["email"] != user.email:
            if await self._user_repo.email_exists(update_data["email"]):
                raise ConflictError(
                    message=f"Email '{update_data['email']}' is already in use",
                    error_code="EMAIL_ALREADY_EXISTS",
                )

        # Apply update
        updated_user = await self._user_repo.update(user_id, **update_data)

        # Audit (especially important for role changes)
        await self._audit_repo.create(
            action="user.update",
            user_id=updated_by,
            resource_type="user",
            resource_id=user_id,
            old_values=old_values,
            new_values=update_data,
            ip_address=ip_address,
        )

        logger.info(
            "user_updated",
            user_id=str(user_id),
            updated_by=str(updated_by),
            changed_fields=list(update_data.keys()),
        )

        return UserResponse.model_validate(updated_user)

    async def deactivate_user(
        self,
        user_id: uuid.UUID,
        deactivated_by: uuid.UUID,
        ip_address: str | None = None,
    ) -> UserResponse:
        """
        Deactivate a user account (soft-delete + status change).

        Deactivated users cannot log in but their data is preserved.
        This is the standard approach at financial institutions —
        accounts are never truly deleted.
        """
        user = await self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(resource="User", resource_id=str(user_id))

        # Prevent self-deactivation
        if user_id == deactivated_by:
            raise ValidationError(
                message="Cannot deactivate your own account",
                error_code="SELF_DEACTIVATION",
            )

        updated_user = await self._user_repo.update(
            user_id, status="inactive"
        )

        # Audit
        await self._audit_repo.create(
            action="user.deactivate",
            user_id=deactivated_by,
            resource_type="user",
            resource_id=user_id,
            old_values={"status": "active"},
            new_values={"status": "inactive"},
            ip_address=ip_address,
        )

        logger.info(
            "user_deactivated",
            user_id=str(user_id),
            deactivated_by=str(deactivated_by),
        )

        return UserResponse.model_validate(updated_user)
