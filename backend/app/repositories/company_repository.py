"""
DealOS AI — Company Repository.

Data access layer for company CRUD operations.
Extends the generic CRUDRepository with company-specific queries.
"""

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company import Company
from app.models.document import Document
from app.models.report import Report
from app.models.risk_finding import RiskFinding
from app.repositories.base import CRUDRepository


class CompanyRepository(CRUDRepository[Company]):
    """Company-specific data access methods."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Company, session)

    async def search_by_name(self, query: str, limit: int = 20) -> list[Company]:
        """Search companies by name (case-insensitive partial match)."""
        stmt = (
            select(Company)
            .where(
                Company.is_deleted == False,  # noqa: E712
                Company.name.ilike(f"%{query}%"),
            )
            .order_by(Company.name.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_ticker(self, ticker: str) -> Company | None:
        """Get a company by its stock ticker symbol."""
        stmt = select(Company).where(
            Company.is_deleted == False,  # noqa: E712
            Company.ticker == ticker.upper(),
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_stats(self, company_id: UUID) -> dict[str, Any] | None:
        """
        Get a company with aggregated statistics.

        Returns a dict with the company and counts of related entities.
        """
        company = await self.get_by_id(company_id)
        if company is None:
            return None

        # Count documents
        doc_count_stmt = (
            select(func.count())
            .select_from(Document)
            .where(
                Document.company_id == company_id,
                Document.is_deleted == False,  # noqa: E712
            )
        )
        doc_count_result = await self._session.execute(doc_count_stmt)
        doc_count = doc_count_result.scalar_one()

        # Count processed documents
        processed_doc_stmt = (
            select(func.count())
            .select_from(Document)
            .where(
                Document.company_id == company_id,
                Document.is_deleted == False,  # noqa: E712
                Document.status == "processed",
            )
        )
        processed_doc_result = await self._session.execute(processed_doc_stmt)
        processed_doc_count = processed_doc_result.scalar_one()

        # Count risk findings
        risk_count_stmt = (
            select(func.count())
            .select_from(RiskFinding)
            .where(
                RiskFinding.company_id == company_id,
                RiskFinding.is_deleted == False,  # noqa: E712
            )
        )
        risk_count_result = await self._session.execute(risk_count_stmt)
        risk_count = risk_count_result.scalar_one()

        # Count reports
        report_count_stmt = (
            select(func.count())
            .select_from(Report)
            .where(
                Report.company_id == company_id,
                Report.is_deleted == False,  # noqa: E712
            )
        )
        report_count_result = await self._session.execute(report_count_stmt)
        report_count = report_count_result.scalar_one()

        return {
            "company": company,
            "document_count": doc_count,
            "processed_document_count": processed_doc_count,
            "risk_finding_count": risk_count,
            "report_count": report_count,
        }

    async def list_for_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Company], int]:
        """
        List companies created by a specific user with total count.

        Returns (companies, total_count) tuple for pagination.
        """
        base_filter = [
            Company.is_deleted == False,  # noqa: E712
            Company.created_by == user_id,
        ]

        # Get total count
        count_stmt = (
            select(func.count())
            .select_from(Company)
            .where(*base_filter)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        # Get paginated results
        stmt = (
            select(Company)
            .where(*base_filter)
            .order_by(Company.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        companies = list(result.scalars().all())

        return companies, total
