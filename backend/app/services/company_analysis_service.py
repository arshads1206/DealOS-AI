"""
DealOS AI — Company Analysis Service.

Orchestrates the company intelligence pipeline:
    Hybrid Retrieval → GPT-4o Profile Extraction → Company Record Update → API Response

Reuses the existing SearchService for context retrieval.
Stores the structured profile in the Company.metadata_ JSONB column
and updates the Company.industry and Company.description fields.
"""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.extractors.company_extractor import CompanyExtractor
from app.core.exceptions import NotFoundError
from app.repositories.company_repository import CompanyRepository
from app.schemas.company_intelligence import CompanyProfileResponse, ExtractedCompanyProfile
from app.schemas.search import SearchRequest
from app.services.search_service import SearchService

logger = structlog.get_logger(__name__)

# Domain-specific retrieval queries for company profiling
COMPANY_QUERIES = [
    "company overview business description who we are what we do",
    "products services solutions offerings portfolio",
    "business segments divisions operating units reportable segments",
    "geographic presence countries operations international markets",
    "customers clients major accounts key relationships",
    "competition competitors market position competitive landscape",
    "employees workforce headcount team size",
    "company history founded headquarters incorporated",
]


class CompanyAnalysisService:
    """
    Company intelligence pipeline orchestrator.

    Pipeline: Retrieve Context → Extract Profile → Update Company Record → Return Response
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._company_repo = CompanyRepository(session)
        self._search_service = SearchService(session)
        self._extractor = CompanyExtractor()

    async def run_analysis(self, company_id: UUID) -> CompanyProfileResponse:
        """
        Run company profile extraction.

        Args:
            company_id: Company to analyze.

        Returns:
            CompanyProfileResponse with extracted company intelligence.

        Raises:
            NotFoundError: If company not found.
        """
        logger.info("company_analysis_start", company_id=str(company_id))

        # ── Validate company exists ──
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        # ── Step 1: Retrieve company context ──
        context = await self._retrieve_company_context(company_id)

        if not context:
            logger.warning("company_analysis_no_context", company_id=str(company_id))
            return CompanyProfileResponse(
                company_id=str(company_id),
                name=company.name,
                ticker=company.ticker,
                industry=company.industry,
                status="no_data",
            )

        # ── Step 2: Extract profile via GPT-4o ──
        profile = await self._extractor.extract(context)

        if profile is None:
            logger.warning("company_analysis_extraction_failed", company_id=str(company_id))
            return CompanyProfileResponse(
                company_id=str(company_id),
                name=company.name,
                ticker=company.ticker,
                industry=company.industry,
                status="partial",
            )

        # ── Step 3: Update company record ──
        await self._update_company_record(company_id, profile)

        # ── Step 4: Format response ──
        logger.info(
            "company_analysis_complete",
            company_id=str(company_id),
            industry=profile.industry,
            products=len(profile.products),
            segments=len(profile.business_segments),
        )

        return CompanyProfileResponse(
            company_id=str(company_id),
            name=company.name,
            ticker=company.ticker,
            business_summary=profile.business_summary,
            industry=profile.industry,
            sector=profile.sector,
            products=profile.products,
            business_segments=profile.business_segments,
            countries=profile.countries,
            major_customers=profile.major_customers,
            major_competitors=profile.major_competitors,
            employee_count=profile.employee_count,
            founded_year=profile.founded_year,
            headquarters=profile.headquarters,
            status="completed",
        )

    async def get_profile(self, company_id: UUID) -> CompanyProfileResponse:
        """
        Retrieve stored company profile from the database.

        Args:
            company_id: Company to retrieve profile for.

        Returns:
            CompanyProfileResponse with stored company intelligence.
        """
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        # Extract profile data from Company.metadata_ JSONB
        metadata = company.metadata_ or {}
        ai_profile = metadata.get("ai_profile", {})

        if not ai_profile:
            return CompanyProfileResponse(
                company_id=str(company_id),
                name=company.name,
                ticker=company.ticker,
                industry=company.industry,
                sector=company.sector,
                business_summary=company.description,
                status="no_data",
            )

        return CompanyProfileResponse(
            company_id=str(company_id),
            name=company.name,
            ticker=company.ticker,
            business_summary=ai_profile.get("business_summary", company.description),
            industry=company.industry,
            sector=company.sector,
            products=ai_profile.get("products", []),
            business_segments=ai_profile.get("business_segments", []),
            countries=ai_profile.get("countries", []),
            major_customers=ai_profile.get("major_customers", []),
            major_competitors=ai_profile.get("major_competitors", []),
            employee_count=ai_profile.get("employee_count"),
            founded_year=ai_profile.get("founded_year"),
            headquarters=ai_profile.get("headquarters"),
            status="completed",
        )

    async def _retrieve_company_context(self, company_id: UUID) -> str:
        """
        Retrieve company-relevant chunks using the hybrid search engine.

        Runs multiple company-profiling queries and deduplicates results.
        """
        all_content: list[str] = []
        seen_chunk_ids: set[str] = set()

        for query in COMPANY_QUERIES:
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
                    "company_context_query_failed",
                    query=query,
                    error=str(e),
                )
                continue

        logger.info(
            "company_context_retrieved",
            unique_chunks=len(seen_chunk_ids),
            total_chars=sum(len(c) for c in all_content),
        )

        return "\n\n---\n\n".join(all_content)

    async def _update_company_record(
        self,
        company_id: UUID,
        profile: ExtractedCompanyProfile,
    ) -> None:
        """
        Update the company record with extracted intelligence.

        Updates:
        - Company.industry — from extraction
        - Company.description — from business_summary
        - Company.sector — from extraction
        - Company.metadata_["ai_profile"] — full structured profile
        """
        # Build the AI profile dict for JSONB storage
        ai_profile = profile.model_dump()

        # Merge with existing metadata (preserve other keys)
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            return

        existing_metadata = company.metadata_ or {}
        existing_metadata["ai_profile"] = ai_profile

        # Update the company record
        await self._company_repo.update(
            company_id,
            industry=profile.industry,
            sector=profile.sector,
            description=profile.business_summary,
            country=profile.countries[0] if profile.countries else company.country,
            metadata_=existing_metadata,
        )

        logger.info(
            "company_record_updated",
            company_id=str(company_id),
            industry=profile.industry,
        )
