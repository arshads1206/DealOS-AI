"""
DealOS AI — Company Service.

Business logic for company workspace management.
Orchestrates between the repository layer and API layer.
"""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate, CompanyWithStats

logger = structlog.get_logger(__name__)


class CompanyService:
    """Company business logic."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = CompanyRepository(session)
        self._audit_repo = AuditLogRepository(session)

    async def create_company(
        self,
        data: CompanyCreate,
        created_by: uuid.UUID,
    ) -> CompanyResponse:
        """
        Create a new company workspace.

        Business rules:
        - Ticker must be unique if provided
        - Company name need not be unique (multiple deals for same company)
        - Creator is automatically the owner
        """
        # Check ticker uniqueness if provided
        if data.ticker:
            existing = await self._repo.get_by_ticker(data.ticker)
            if existing:
                raise ConflictError(
                    message=f"Company with ticker '{data.ticker}' already exists",
                    error_code="TICKER_ALREADY_EXISTS",
                )

        company = await self._repo.create(
            name=data.name,
            ticker=data.ticker.upper() if data.ticker else None,
            industry=data.industry,
            sector=data.sector,
            description=data.description,
            country=data.country,
            metadata_=data.metadata,
            created_by=created_by,
        )

        # Audit log
        await self._audit_repo.create(
            action="company.create",
            user_id=created_by,
            resource_type="company",
            resource_id=company.id,
            new_values={"name": data.name, "ticker": data.ticker},
        )

        logger.info("company_created", company_id=str(company.id), name=data.name)

        return CompanyResponse.model_validate(company)

    async def get_company(self, company_id: uuid.UUID) -> CompanyResponse:
        """Get a company by ID."""
        company = await self._repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))
        return CompanyResponse.model_validate(company)

    async def get_company_with_stats(self, company_id: uuid.UUID) -> CompanyWithStats:
        """Get a company with aggregated statistics."""
        stats = await self._repo.get_with_stats(company_id)
        if stats is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        company = stats["company"]
        return CompanyWithStats(
            id=company.id,
            name=company.name,
            ticker=company.ticker,
            industry=company.industry,
            sector=company.sector,
            description=company.description,
            country=company.country,
            metadata=company.metadata_,
            created_by=company.created_by,
            created_at=company.created_at,
            updated_at=company.updated_at,
            document_count=stats["document_count"],
            processed_document_count=stats["processed_document_count"],
            risk_finding_count=stats["risk_finding_count"],
            report_count=stats["report_count"],
        )

    async def list_companies(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> tuple[list[CompanyResponse], int]:
        """
        List companies with optional search.

        If search is provided, filters by name (case-insensitive).
        Returns (companies, total_count) for pagination.
        """
        if search:
            companies = await self._repo.search_by_name(search, limit=limit)
            return [CompanyResponse.model_validate(c) for c in companies], len(companies)

        companies = await self._repo.get_all(skip=skip, limit=limit)
        total = await self._repo.count()
        return [CompanyResponse.model_validate(c) for c in companies], total

    async def update_company(
        self,
        company_id: uuid.UUID,
        data: CompanyUpdate,
        updated_by: uuid.UUID,
    ) -> CompanyResponse:
        """Update a company. Only provided fields are updated."""
        company = await self._repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        # Check ticker uniqueness if being changed
        if data.ticker and data.ticker.upper() != company.ticker:
            existing = await self._repo.get_by_ticker(data.ticker)
            if existing:
                raise ConflictError(
                    message=f"Company with ticker '{data.ticker}' already exists",
                    error_code="TICKER_ALREADY_EXISTS",
                )

        update_data = data.model_dump(exclude_unset=True)

        # Handle ticker uppercasing
        if "ticker" in update_data and update_data["ticker"]:
            update_data["ticker"] = update_data["ticker"].upper()

        # Handle metadata field name mapping
        if "metadata" in update_data:
            update_data["metadata_"] = update_data.pop("metadata")

        if update_data:
            old_values = {k: getattr(company, k) for k in update_data}
            company = await self._repo.update(company_id, **update_data)

            # Audit log
            await self._audit_repo.create(
                action="company.update",
                user_id=updated_by,
                resource_type="company",
                resource_id=company_id,
                old_values=old_values,
                new_values=update_data,
            )

            logger.info("company_updated", company_id=str(company_id))

        return CompanyResponse.model_validate(company)

    async def delete_company(
        self,
        company_id: uuid.UUID,
        deleted_by: uuid.UUID,
    ) -> CompanyResponse:
        """Soft-delete a company and its related data."""
        company = await self._repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        await self._repo.soft_delete(company_id)

        # Audit log
        await self._audit_repo.create(
            action="company.delete",
            user_id=deleted_by,
            resource_type="company",
            resource_id=company_id,
        )

        logger.info("company_deleted", company_id=str(company_id))

        return CompanyResponse.model_validate(company)
