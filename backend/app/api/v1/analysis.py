"""
DealOS AI — Analysis API Endpoints.

REST API for the Financial Intelligence and Risk Intelligence subsystems:

POST endpoints (run analysis):
  POST /api/v1/analysis/financial/{company_id}  — Extract financial metrics
  POST /api/v1/analysis/risk/{company_id}       — Detect risk signals
  POST /api/v1/analysis/company/{company_id}    — Generate company profile

GET endpoints (retrieve stored results):
  GET /api/v1/analysis/financial/{company_id}   — Get stored financial metrics
  GET /api/v1/analysis/risk/{company_id}        — Get stored risk findings
  GET /api/v1/analysis/company/{company_id}     — Get stored company profile

All endpoints use RUN_ANALYSIS permission for POST and VIEW_DOCUMENTS for GET.
"""

import uuid

from fastapi import APIRouter, Depends, Query

from app.api.middleware.auth import CurrentUser
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.company_intelligence import CompanyProfileResponse
from app.schemas.financial import FinancialAnalysisRequest, FinancialAnalysisResponse
from app.schemas.risk import RiskAnalysisRequest, RiskAnalysisResponse
from app.services.company_analysis_service import CompanyAnalysisService
from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.risk_analysis_service import RiskAnalysisService

router = APIRouter()


# ═══════════════════════════════════════════════════════════════════
# Financial Analysis
# ═══════════════════════════════════════════════════════════════════


@router.post(
    "/financial/{company_id}",
    response_model=FinancialAnalysisResponse,
    summary="Run financial metric extraction",
    responses={
        200: {"description": "Financial metrics extracted and stored"},
        404: {"description": "Company or document not found"},
    },
)
async def run_financial_analysis(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    request: FinancialAnalysisRequest | None = None,
    _: None = Depends(PermissionChecker(Permission.RUN_ANALYSIS)),
):
    """
    Extract structured financial KPIs from company documents.

    Uses the hybrid retrieval engine to find financial content,
    then GPT-4o to extract metrics like Revenue, EBITDA, Net Income,
    Free Cash Flow, ROE, debt ratios, and more.

    Results are stored in PostgreSQL for future retrieval.
    Re-running clears previous extraction results (idempotent).
    """
    service = FinancialAnalysisService(db)
    return await service.run_analysis(
        company_id=company_id,
        document_id=request.document_id if request else None,
    )


@router.get(
    "/financial/{company_id}",
    response_model=FinancialAnalysisResponse,
    summary="Get stored financial metrics",
    responses={
        200: {"description": "Stored financial metrics for the company"},
        404: {"description": "Company not found"},
    },
)
async def get_financial_metrics(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DOCUMENTS)),
    period: str | None = Query(default=None, description="Filter by period (e.g., 'FY 2023')"),
    metric_name: str | None = Query(default=None, description="Filter by metric name (e.g., 'revenue')"),
):
    """
    Retrieve previously extracted financial metrics for a company.

    Optionally filter by reporting period or metric name.
    Returns an empty list if no analysis has been run yet.
    """
    service = FinancialAnalysisService(db)
    return await service.get_metrics(
        company_id=company_id,
        period=period,
        metric_name=metric_name,
    )


# ═══════════════════════════════════════════════════════════════════
# Risk Analysis
# ═══════════════════════════════════════════════════════════════════


@router.post(
    "/risk/{company_id}",
    response_model=RiskAnalysisResponse,
    summary="Run risk detection analysis",
    responses={
        200: {"description": "Risk findings detected and stored"},
        404: {"description": "Company or document not found"},
    },
)
async def run_risk_analysis(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    request: RiskAnalysisRequest | None = None,
    _: None = Depends(PermissionChecker(Permission.RUN_ANALYSIS)),
):
    """
    Detect risk signals in company documents.

    Analyzes documents for risks including: debt growth, customer/supplier
    concentration, litigation, regulatory issues, auditor changes,
    executive changes, ESG concerns, operational, cybersecurity, and market risks.

    Each risk includes severity, confidence, evidence, and reasoning.
    Results are stored in PostgreSQL for future retrieval.
    """
    service = RiskAnalysisService(db)
    return await service.run_analysis(
        company_id=company_id,
        document_id=request.document_id if request else None,
    )


@router.get(
    "/risk/{company_id}",
    response_model=RiskAnalysisResponse,
    summary="Get stored risk findings",
    responses={
        200: {"description": "Stored risk findings for the company"},
        404: {"description": "Company not found"},
    },
)
async def get_risk_findings(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DOCUMENTS)),
    severity: str | None = Query(default=None, description="Filter by severity (critical/high/medium/low/info)"),
    category: str | None = Query(default=None, description="Filter by risk category"),
):
    """
    Retrieve previously detected risk findings for a company.

    Optionally filter by severity level or risk category.
    Includes a severity summary with counts per level.
    """
    service = RiskAnalysisService(db)
    return await service.get_risks(
        company_id=company_id,
        severity=severity,
        category=category,
    )


# ═══════════════════════════════════════════════════════════════════
# Company Analysis
# ═══════════════════════════════════════════════════════════════════


@router.post(
    "/company/{company_id}",
    response_model=CompanyProfileResponse,
    summary="Generate AI company profile",
    responses={
        200: {"description": "Company profile generated and stored"},
        404: {"description": "Company not found"},
    },
)
async def run_company_analysis(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.RUN_ANALYSIS)),
):
    """
    Generate a comprehensive company profile from documents.

    Extracts business summary, industry classification, products,
    business segments, geographic presence, major customers,
    competitors, and other company intelligence.

    Updates the company record with the extracted profile.
    """
    service = CompanyAnalysisService(db)
    return await service.run_analysis(company_id=company_id)


@router.get(
    "/company/{company_id}",
    response_model=CompanyProfileResponse,
    summary="Get stored company profile",
    responses={
        200: {"description": "Stored company intelligence profile"},
        404: {"description": "Company not found"},
    },
)
async def get_company_profile(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DOCUMENTS)),
):
    """
    Retrieve the AI-generated company profile.

    Returns the stored company intelligence including business summary,
    products, segments, competitors, and other structured data.
    """
    service = CompanyAnalysisService(db)
    return await service.get_profile(company_id=company_id)
