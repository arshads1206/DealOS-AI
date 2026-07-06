"""
DealOS AI — Audit Log Repository.

Append-only data access for audit trail entries.

Unlike other repositories, AuditLogRepository:
- Does NOT support update or delete (audit logs are immutable)
- Always creates logs within the existing transaction (no separate commit)
- Provides query methods filtered by user, action, resource, and time range

This is critical for SOX compliance at financial institutions.
"""

import uuid
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog


class AuditLogRepository:
    """
    Append-only audit log data access.

    Does NOT extend CRUDRepository because audit logs:
    - Cannot be updated or deleted
    - Don't have soft-delete semantics
    - Have different query patterns (time-range, action filtering)
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> AuditLog:
        """
        Create an immutable audit log entry.

        This runs within the caller's transaction — if the parent operation
        rolls back, the audit log also rolls back (correct behavior: we don't
        want audit entries for operations that didn't succeed).
        """
        log = AuditLog(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        self._session.add(log)
        await self._session.flush()
        return log

    async def get_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get audit logs for a specific user, most recent first."""
        query = (
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_resource(
        self,
        resource_type: str,
        resource_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get audit logs for a specific resource."""
        query = (
            select(AuditLog)
            .where(AuditLog.resource_type == resource_type)
            .where(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AuditLog]:
        """Get audit logs for a specific action type."""
        query = (
            select(AuditLog)
            .where(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_recent(self, limit: int = 100) -> list[AuditLog]:
        """Get the most recent audit log entries."""
        query = (
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def count_by_action(self, action: str) -> int:
        """Count audit entries for a specific action."""
        query = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.action == action)
        )
        result = await self._session.execute(query)
        return result.scalar_one()
