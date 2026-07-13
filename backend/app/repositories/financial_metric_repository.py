"""
DealOS AI — Financial Metric Repository.

Data access layer for structured financial KPIs.
Extends CRUDRepository with financial-domain queries:
filtering by company, period, metric name, and bulk operations.
"""

from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_metric import FinancialMetric
from app.repositories.base import CRUDRepository


class FinancialMetricRepository(CRUDRepository[FinancialMetric]):
    """Financial metric data access with domain-specific queries."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(FinancialMetric, session)

    async def create_bulk(self, metrics: list[dict]) -> list[FinancialMetric]:
        """
        Bulk insert financial metrics from an extraction run.

        Args:
            metrics: List of metric dicts matching FinancialMetric columns.
        """
        metric_objects = [FinancialMetric(**m) for m in metrics]
        self._session.add_all(metric_objects)
        await self._session.flush()
        return metric_objects

    async def get_by_company(
        self,
        company_id: UUID,
        period: str | None = None,
        metric_name: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FinancialMetric]:
        """
        Get financial metrics for a company with optional filters.

        Args:
            company_id: Company to retrieve metrics for.
            period: Optional filter by period (e.g., "FY 2023").
            metric_name: Optional filter by metric name (e.g., "revenue").
            skip: Pagination offset.
            limit: Maximum results.
        """
        stmt = (
            select(FinancialMetric)
            .where(
                FinancialMetric.company_id == company_id,
                FinancialMetric.is_deleted == False,  # noqa: E712
            )
        )

        if period:
            stmt = stmt.where(FinancialMetric.period == period)
        if metric_name:
            stmt = stmt.where(FinancialMetric.metric_name == metric_name)

        stmt = (
            stmt.order_by(
                FinancialMetric.period.desc(),
                FinancialMetric.metric_name.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_latest_by_company(
        self,
        company_id: UUID,
        limit: int = 50,
    ) -> list[FinancialMetric]:
        """
        Get the most recently extracted metrics for a company.

        Returns the latest extraction batch ordered by creation time.
        """
        stmt = (
            select(FinancialMetric)
            .where(
                FinancialMetric.company_id == company_id,
                FinancialMetric.is_deleted == False,  # noqa: E712
            )
            .order_by(FinancialMetric.created_at.desc())
            .limit(limit)
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_document(self, document_id: UUID) -> int:
        """
        Delete all metrics extracted from a specific document.

        Used for idempotent re-extraction — clear previous results
        before storing a new extraction run.
        """
        stmt = (
            delete(FinancialMetric)
            .where(FinancialMetric.document_id == document_id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def count_by_company(self, company_id: UUID) -> int:
        """Count total metrics for a company."""
        stmt = (
            select(func.count())
            .select_from(FinancialMetric)
            .where(
                FinancialMetric.company_id == company_id,
                FinancialMetric.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
