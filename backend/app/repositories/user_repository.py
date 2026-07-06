"""
DealOS AI — User Repository.

Data access layer for User operations.
Extends the generic CRUDRepository with user-specific queries.

Why a dedicated repository instead of just using CRUDRepository[User]?
- get_by_email is the most common query (login) — deserves a named method
- Email uniqueness check is needed during registration
- Last login timestamp update is a frequent operation
- Keeps SQL concerns out of the service layer
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import CRUDRepository


class UserRepository(CRUDRepository[User]):
    """User-specific data access operations."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """
        Find a user by email address.

        Used during login — the primary lookup path for authentication.
        Email is indexed and unique, so this is an O(1) lookup.
        """
        query = (
            select(User)
            .where(User.email == email)
            .where(User.is_deleted == False)  # noqa: E712
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if an email is already registered.

        Used during registration to provide a clear error message
        instead of a database constraint violation.
        """
        query = (
            select(func.count())
            .select_from(User)
            .where(User.email == email)
            .where(User.is_deleted == False)  # noqa: E712
        )
        result = await self._session.execute(query)
        count = result.scalar_one()
        return count > 0

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """
        Update the last_login_at timestamp.

        Called after successful authentication. Useful for:
        - Security auditing (detect dormant accounts)
        - Session management
        - User activity tracking
        """
        user = await self.get_by_id(user_id)
        if user:
            user.last_login_at = datetime.now(timezone.utc)
            await self._session.flush()

    async def get_active_users(
        self, skip: int = 0, limit: int = 20
    ) -> list[User]:
        """Get paginated list of active (non-deleted, non-suspended) users."""
        query = (
            select(User)
            .where(User.is_deleted == False)  # noqa: E712
            .where(User.status == "active")
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_by_role(self, role: str) -> int:
        """Count users with a specific role."""
        query = (
            select(func.count())
            .select_from(User)
            .where(User.role == role)
            .where(User.is_deleted == False)  # noqa: E712
        )
        result = await self._session.execute(query)
        return result.scalar_one()
