"""
DealOS AI — Company Management Endpoints.

REST API for company workspace CRUD:
- POST /companies — Create a new company workspace
- GET /companies — List all companies (paginated, searchable)
- GET /companies/{id} — Get company details with stats
- PATCH /companies/{id} — Update company
- DELETE /companies/{id} — Soft delete company
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.middleware.auth import CurrentUser
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate, CompanyWithStats
from app.services.company_service import CompanyService

router = APIRouter()


@router.post(
    "/",
    response_model=CompanyResponse,
    status_code=201,
    summary="Create a new company workspace",
    responses={
        201: {"description": "Company created successfully"},
        409: {"description": "Ticker already exists"},
    },
)
async def create_company(
    data: CompanyCreate,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.CREATE_COMPANY)),
):
    """
    Create a new company workspace for due diligence.

    Requires the `create_company` permission (admin or analyst).
    If a ticker is provided, it must be unique across the platform.
    """
    service = CompanyService(db)
    return await service.create_company(
        data=data,
        created_by=uuid.UUID(current_user["user_id"]),
    )


@router.get(
    "/",
    response_model=PaginatedResponse[CompanyResponse],
    summary="List all companies",
    responses={
        200: {"description": "Paginated company list"},
    },
)
async def list_companies(
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DASHBOARD)),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    search: str | None = Query(default=None, description="Search by company name"),
):
    """
    List all companies with pagination and optional search.

    Requires the `view_dashboard` permission (all authenticated roles).
    """
    service = CompanyService(db)
    skip = (page - 1) * page_size
    companies, total = await service.list_companies(
        skip=skip, limit=page_size, search=search
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=companies,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{company_id}",
    response_model=CompanyWithStats,
    summary="Get company details with stats",
    responses={
        200: {"description": "Company details with aggregated statistics"},
        404: {"description": "Company not found"},
    },
)
async def get_company(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DASHBOARD)),
):
    """
    Get detailed company information including document and analysis counts.

    Returns aggregated stats: total documents, processed documents,
    risk findings, and report counts.
    """
    service = CompanyService(db)
    return await service.get_company_with_stats(company_id)


@router.patch(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Update company",
    responses={
        200: {"description": "Company updated"},
        404: {"description": "Company not found"},
        409: {"description": "Ticker already in use"},
    },
)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.CREATE_COMPANY)),
):
    """
    Update a company's information.

    Only provided fields are updated (PATCH semantics).
    Requires `create_company` permission.
    """
    service = CompanyService(db)
    return await service.update_company(
        company_id=company_id,
        data=data,
        updated_by=uuid.UUID(current_user["user_id"]),
    )


@router.delete(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Delete company (soft delete)",
    responses={
        200: {"description": "Company deactivated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Company not found"},
    },
)
async def delete_company(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.DELETE_RESOURCES)),
):
    """
    Soft-delete a company workspace.

    The company and its data are preserved but hidden from normal queries.
    Requires `delete_resources` permission (admin only).
    """
    service = CompanyService(db)
    return await service.delete_company(
        company_id=company_id,
        deleted_by=uuid.UUID(current_user["user_id"]),
    )
