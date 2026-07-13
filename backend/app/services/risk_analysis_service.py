"""
DealOS AI — Risk Analysis Service.

Orchestrates the risk intelligence pipeline:
    Hybrid Retrieval → GPT-4o Risk Detection → PostgreSQL Storage → API Response

Reuses the existing SearchService for context retrieval.
Idempotent: clears previous risk findings before re-analyzing.
"""

import uuid
from decimal import Decimal
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.extractors.risk_extractor import RiskExtractor
from app.core.exceptions import NotFoundError
from app.repositories.company_repository import CompanyRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.risk_finding_repository import RiskFindingRepository
from app.schemas.risk import (
    RiskAnalysisResponse,
    RiskExtractionResult,
    RiskFindingResponse,
    SeveritySummary,
)
from app.schemas.search import SearchRequest
from app.services.search_service import SearchService

logger = structlog.get_logger(__name__)

# Domain-specific retrieval queries for risk context
RISK_QUERIES = [
    "risk factors material risks uncertainties threats challenges",
    "litigation legal proceedings lawsuits settlements regulatory investigation",
    "debt leverage covenant borrowing credit rating default",
    "customer concentration major customers revenue dependency",
    "supplier concentration supply chain dependency single source",
    "auditor change accounting restatement internal controls weakness",
    "executive officer departure resignation appointment management change",
    "environmental social governance ESG sustainability climate",
    "cybersecurity data breach privacy security vulnerability incident",
    "competition market disruption demand decline pricing pressure",
]


class RiskAnalysisService:
    """
    Risk intelligence pipeline orchestrator.

    Pipeline: Retrieve Context → Detect Risks → Store in DB → Return Response
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._company_repo = CompanyRepository(session)
        self._document_repo = DocumentRepository(session)
        self._risk_repo = RiskFindingRepository(session)
        self._search_service = SearchService(session)
        self._extractor = RiskExtractor()

    async def run_analysis(
        self,
        company_id: UUID,
        document_id: UUID | None = None,
    ) -> RiskAnalysisResponse:
        """
        Run risk detection for a company.

        Args:
            company_id: Company to analyze.
            document_id: Optional — restrict to a specific document.

        Returns:
            RiskAnalysisResponse with detected risk findings.

        Raises:
            NotFoundError: If company or document not found.
        """
        logger.info(
            "risk_analysis_start",
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

        # ── Step 1: Retrieve risk-relevant context ──
        context = await self._retrieve_risk_context(company_id)

        if not context:
            logger.warning("risk_analysis_no_context", company_id=str(company_id))
            return RiskAnalysisResponse(
                company_id=str(company_id),
                risks=[],
                total_risks=0,
                severity_summary=SeveritySummary(),
                status="no_data",
            )

        # ── Step 2: Extract risks via GPT-4o ──
        extraction_result = await self._extractor.extract(context)

        if not extraction_result.risks:
            logger.warning("risk_analysis_no_risks", company_id=str(company_id))
            return RiskAnalysisResponse(
                company_id=str(company_id),
                risks=[],
                total_risks=0,
                severity_summary=SeveritySummary(),
                status="no_data",
            )

        # ── Step 3: Store in PostgreSQL ──
        source_document_id = document_id or await self._get_primary_document(company_id)

        if source_document_id:
            deleted_count = await self._risk_repo.delete_by_document(source_document_id)
            if deleted_count > 0:
                logger.info(
                    "risk_analysis_cleared_previous",
                    document_id=str(source_document_id),
                    deleted=deleted_count,
                )

        stored_risks = await self._store_risks(
            extraction_result,
            company_id,
            source_document_id or uuid.uuid4(),
        )

        # ── Step 4: Build severity summary ──
        severity_summary = await self._risk_repo.get_severity_summary(company_id)

        # ── Step 5: Format response ──
        risk_responses = [
            RiskFindingResponse.model_validate(r) for r in stored_risks
        ]

        logger.info(
            "risk_analysis_complete",
            company_id=str(company_id),
            risks_stored=len(risk_responses),
            severity_summary=severity_summary,
        )

        return RiskAnalysisResponse(
            company_id=str(company_id),
            risks=risk_responses,
            total_risks=len(risk_responses),
            severity_summary=SeveritySummary(**severity_summary),
            status="completed",
        )

    async def get_risks(
        self,
        company_id: UUID,
        severity: str | None = None,
        category: str | None = None,
    ) -> RiskAnalysisResponse:
        """
        Retrieve stored risk findings for a company.

        Args:
            company_id: Company to retrieve risks for.
            severity: Optional filter by severity level.
            category: Optional filter by risk category.

        Returns:
            RiskAnalysisResponse with stored risks and severity summary.
        """
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        risks = await self._risk_repo.get_by_company(
            company_id=company_id,
            severity=severity,
            category=category,
        )

        severity_summary = await self._risk_repo.get_severity_summary(company_id)

        risk_responses = [
            RiskFindingResponse.model_validate(r) for r in risks
        ]

        return RiskAnalysisResponse(
            company_id=str(company_id),
            risks=risk_responses,
            total_risks=len(risk_responses),
            severity_summary=SeveritySummary(**severity_summary),
            status="completed" if risk_responses else "no_data",
        )

    async def _retrieve_risk_context(self, company_id: UUID) -> str:
        """
        Retrieve risk-relevant chunks using the hybrid search engine.

        Runs multiple risk-specific queries and deduplicates results.
        """
        all_content: list[str] = []
        seen_chunk_ids: set[str] = set()

        for query in RISK_QUERIES:
            try:
                search_request = SearchRequest(
                    question=query,
                    company_id=company_id,
                    top_k=8,
                )
                response = await self._search_service.search(search_request)

                for result in response.results:
                    if result.chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(result.chunk_id)
                        all_content.append(result.content)
            except Exception as e:
                logger.warning(
                    "risk_context_query_failed",
                    query=query,
                    error=str(e),
                )
                continue

        logger.info(
            "risk_context_retrieved",
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
        return result.scalar_one_or_none()

    async def _store_risks(
        self,
        extraction: RiskExtractionResult,
        company_id: UUID,
        document_id: UUID,
    ) -> list:
        """Convert extracted risks to DB records and bulk insert."""
        risk_dicts = [
            {
                "risk_category": r.risk_category,
                "risk_subcategory": r.risk_subcategory,
                "title": r.title,
                "description": r.description,
                "severity": r.severity,
                "confidence": Decimal(str(r.confidence)),
                "evidence": r.evidence,
                "reasoning": r.reasoning,
                "source_page": r.source_page,
                "company_id": company_id,
                "document_id": document_id,
            }
            for r in extraction.risks
        ]

        return await self._risk_repo.create_bulk(risk_dicts)
