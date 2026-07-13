"""
DealOS AI — Financial Analysis Service.

Orchestrates the financial intelligence pipeline:
    Hybrid Retrieval → GPT-4o Extraction → PostgreSQL Storage → API Response

Reuses the existing SearchService for context retrieval — no duplicated
retrieval logic. Idempotent: clears previous extraction results before
re-extracting for the same scope.
"""

import uuid
from decimal import Decimal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.extractors.financial_extractor import FinancialExtractor
from app.core.exceptions import NotFoundError
from app.repositories.company_repository import CompanyRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.financial_metric_repository import FinancialMetricRepository
from app.schemas.financial import (
    ExtractionResult,
    FinancialAnalysisResponse,
    FinancialMetricResponse,
)
from app.schemas.search import SearchRequest
from app.services.search_service import SearchService

logger = structlog.get_logger(__name__)

# Domain-specific retrieval queries for financial context
FINANCIAL_QUERIES = [
    "revenue total sales gross profit operating income net income earnings",
    "EBITDA operating cash flow free cash flow capital expenditure CAPEX",
    "debt total liabilities cash equivalents current ratio debt to equity",
    "gross margin operating margin return on equity ROE ROCE",
    "segment revenue geographic revenue fiscal year quarterly results",
]


class FinancialAnalysisService:
    """
    Financial intelligence pipeline orchestrator.

    Pipeline: Retrieve Context → Extract Metrics → Store in DB → Return Response
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._company_repo = CompanyRepository(session)
        self._document_repo = DocumentRepository(session)
        self._metric_repo = FinancialMetricRepository(session)
        self._search_service = SearchService(session)
        self._extractor = FinancialExtractor()

    async def run_analysis(
        self,
        company_id: UUID,
        document_id: UUID | None = None,
    ) -> FinancialAnalysisResponse:
        """
        Run financial metric extraction for a company.

        Args:
            company_id: Company to analyze.
            document_id: Optional — restrict to a specific document.

        Returns:
            FinancialAnalysisResponse with extracted metrics.

        Raises:
            NotFoundError: If company or document not found.
        """
        logger.info(
            "financial_analysis_start",
            company_id=str(company_id),
            document_id=str(document_id) if document_id else None,
        )

        # ── Validate company exists ──
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        # ── Validate document if specified ──
        if document_id:
            doc = await self._document_repo.get_by_id(document_id)
            if doc is None:
                raise NotFoundError(resource="Document", resource_id=str(document_id))

        # ── Step 1: Retrieve financial context using hybrid search ──
        context = await self._retrieve_financial_context(company_id)

        if not context:
            logger.warning("financial_analysis_no_context", company_id=str(company_id))
            return FinancialAnalysisResponse(
                company_id=str(company_id),
                metrics=[],
                total_metrics=0,
                status="no_data",
            )

        # ── Step 2: Extract metrics via GPT-4o ──
        extraction_result = await self._extractor.extract(context)

        if not extraction_result.metrics:
            logger.warning("financial_analysis_no_metrics", company_id=str(company_id))
            return FinancialAnalysisResponse(
                company_id=str(company_id),
                metrics=[],
                total_metrics=0,
                status="no_data",
            )

        # ── Step 3: Store in PostgreSQL ──
        # Find the most relevant document for provenance tracking
        source_document_id = document_id or await self._get_primary_document(company_id)

        if source_document_id:
            # Idempotent: clear previous extraction for this document
            deleted_count = await self._metric_repo.delete_by_document(source_document_id)
            if deleted_count > 0:
                logger.info(
                    "financial_analysis_cleared_previous",
                    document_id=str(source_document_id),
                    deleted=deleted_count,
                )

        stored_metrics = await self._store_metrics(
            extraction_result,
            company_id,
            source_document_id or uuid.uuid4(),  # Fallback for edge case
        )

        # ── Step 4: Format response ──
        metric_responses = [
            FinancialMetricResponse.model_validate(m) for m in stored_metrics
        ]

        logger.info(
            "financial_analysis_complete",
            company_id=str(company_id),
            metrics_stored=len(metric_responses),
        )

        return FinancialAnalysisResponse(
            company_id=str(company_id),
            metrics=metric_responses,
            total_metrics=len(metric_responses),
            fiscal_year=extraction_result.fiscal_year,
            reporting_currency=extraction_result.reporting_currency,
            status="completed",
        )

    async def get_metrics(
        self,
        company_id: UUID,
        period: str | None = None,
        metric_name: str | None = None,
    ) -> FinancialAnalysisResponse:
        """
        Retrieve stored financial metrics for a company.

        Args:
            company_id: Company to retrieve metrics for.
            period: Optional filter by period.
            metric_name: Optional filter by metric name.

        Returns:
            FinancialAnalysisResponse with stored metrics.
        """
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        metrics = await self._metric_repo.get_by_company(
            company_id=company_id,
            period=period,
            metric_name=metric_name,
        )

        metric_responses = [
            FinancialMetricResponse.model_validate(m) for m in metrics
        ]

        return FinancialAnalysisResponse(
            company_id=str(company_id),
            metrics=metric_responses,
            total_metrics=len(metric_responses),
            status="completed" if metric_responses else "no_data",
        )

    async def _retrieve_financial_context(self, company_id: UUID) -> str:
        """
        Retrieve financial-relevant chunks using the hybrid search engine.

        Runs multiple domain-specific queries and concatenates the
        unique results for maximum coverage.
        """
        all_content: list[str] = []
        seen_chunk_ids: set[str] = set()

        for query in FINANCIAL_QUERIES:
            try:
                search_request = SearchRequest(
                    question=query,
                    company_id=company_id,
                    top_k=10,
                )
                response = await self._search_service.search(search_request)

                for result in response.results:
                    if result.chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(result.chunk_id)
                        all_content.append(result.content)
            except Exception as e:
                logger.warning(
                    "financial_context_query_failed",
                    query=query,
                    error=str(e),
                )
                continue

        logger.info(
            "financial_context_retrieved",
            unique_chunks=len(seen_chunk_ids),
            total_chars=sum(len(c) for c in all_content),
        )

        return "\n\n---\n\n".join(all_content)

    async def _get_primary_document(self, company_id: UUID) -> UUID | None:
        """Get the first processed document for a company (for provenance)."""
        from sqlalchemy import select
        from app.models.document import Document

        stmt = (
            select(Document.id)
            .where(
                Document.company_id == company_id,
                Document.is_deleted == False,  # noqa: E712
                Document.status == "processed",
            )
            .order_by(Document.created_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()
        return row

    async def _store_metrics(
        self,
        extraction: ExtractionResult,
        company_id: UUID,
        document_id: UUID,
    ) -> list:
        """Convert extracted metrics to DB records and bulk insert."""
        metric_dicts = [
            {
                "metric_name": m.metric_name,
                "metric_value": Decimal(str(m.metric_value)),
                "currency": m.currency,
                "unit": m.unit,
                "period": m.period,
                "period_type": m.period_type,
                "confidence": Decimal(str(m.confidence)),
                "source_text": m.source_text,
                "source_page": m.source_page,
                "company_id": company_id,
                "document_id": document_id,
            }
            for m in extraction.metrics
        ]

        return await self._metric_repo.create_bulk(metric_dicts)
