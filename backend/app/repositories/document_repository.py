"""
DealOS AI — Document Repository.

Data access layer for document CRUD operations.
Extends the generic CRUDRepository with document-specific queries.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import DocumentStatus
from app.models.document import Document
from app.repositories.base import CRUDRepository


class DocumentRepository(CRUDRepository[Document]):
    """Document-specific data access methods."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Document, session)

    async def get_by_company(
        self,
        company_id: UUID,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> tuple[list[Document], int]:
        """
        List documents for a company with optional status filter.

        Returns (documents, total_count) tuple for pagination.
        """
        base_filter = [
            Document.company_id == company_id,
            Document.is_deleted == False,  # noqa: E712
        ]
        if status:
            base_filter.append(Document.status == status)

        # Total count
        count_stmt = (
            select(func.count())
            .select_from(Document)
            .where(*base_filter)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()

        # Paginated results
        stmt = (
            select(Document)
            .where(*base_filter)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        documents = list(result.scalars().all())

        return documents, total

    async def update_status(
        self,
        document_id: UUID,
        status: str,
        error_message: str | None = None,
    ) -> Document | None:
        """Update document processing status."""
        update_data = {"status": status}
        if error_message is not None:
            update_data["error_message"] = error_message
        return await self.update(document_id, **update_data)

    async def get_processing_stats(self, company_id: UUID) -> dict[str, int]:
        """Get document processing statistics for a company."""
        stats = {}
        for status in DocumentStatus:
            stmt = (
                select(func.count())
                .select_from(Document)
                .where(
                    Document.company_id == company_id,
                    Document.is_deleted == False,  # noqa: E712
                    Document.status == status.value,
                )
            )
            result = await self._session.execute(stmt)
            stats[status.value] = result.scalar_one()
        return stats

    async def get_unprocessed(self, limit: int = 10) -> list[Document]:
        """Get documents waiting to be processed."""
        stmt = (
            select(Document)
            .where(
                Document.is_deleted == False,  # noqa: E712
                Document.status == DocumentStatus.UPLOADED,
            )
            .order_by(Document.created_at.asc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
