"""
DealOS AI — Risk Finding Repository.

Data access layer for detected risk signals.
Extends CRUDRepository with risk-domain queries:
filtering by company, severity, category, severity summaries, and bulk operations.
"""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk_finding import RiskFinding
from app.repositories.base import CRUDRepository


class RiskFindingRepository(CRUDRepository[RiskFinding]):
    """Risk finding data access with domain-specific queries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RiskFinding, session)

    async def create_bulk(self, risks: list[dict]) -> list[RiskFinding]:
        """
        Bulk insert risk findings from an extraction run.

        Args:
            risks: List of risk dicts matching RiskFinding columns.
        """
        risk_objects = [RiskFinding(**r) for r in risks]
        self._session.add_all(risk_objects)
        await self._session.flush()
        return risk_objects

    async def get_by_company(
        self,
        company_id: UUID,
        severity: str | None = None,
        category: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[RiskFinding]:
        """
        Get risk findings for a company with optional filters.

        Args:
            company_id: Company to retrieve risks for.
            severity: Optional filter by severity level.
            category: Optional filter by risk category.
            skip: Pagination offset.
            limit: Maximum results.
        """
        stmt = (
            select(RiskFinding)
            .where(
                RiskFinding.company_id == company_id,
                RiskFinding.is_deleted == False,  # noqa: E712
            )
        )

        if severity:
            stmt = stmt.where(RiskFinding.severity == severity)
        if category:
            stmt = stmt.where(RiskFinding.risk_category == category)

        stmt = (
            stmt.order_by(
                RiskFinding.detected_at.desc(),
                RiskFinding.severity.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_severity_summary(self, company_id: UUID) -> dict[str, int]:
        """
        Get risk count grouped by severity for a company.

        Returns a dict like {"critical": 2, "high": 5, "medium": 8, ...}.
        """
        stmt = (
            select(
                RiskFinding.severity,
                func.count().label("count"),
            )
            .where(
                RiskFinding.company_id == company_id,
                RiskFinding.is_deleted == False,  # noqa: E712
            )
            .group_by(RiskFinding.severity)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        # Initialize all severity levels to 0
        summary = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for row in rows:
            if row.severity in summary:
                summary[row.severity] = row.count

        return summary

    async def delete_by_document(self, document_id: UUID) -> int:
        """
        Delete all risk findings from a specific document.

        Used for idempotent re-extraction.
        """
        stmt = (
            delete(RiskFinding)
            .where(RiskFinding.document_id == document_id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def count_by_company(self, company_id: UUID) -> int:
        """Count total risk findings for a company."""
        stmt = (
            select(func.count())
            .select_from(RiskFinding)
            .where(
                RiskFinding.company_id == company_id,
                RiskFinding.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
