"""
DealOS AI — Company Intelligence Schemas.

Pydantic models for AI-generated company profiles.

The company extractor produces a structured business profile from
document content — business summary, products, segments, competitors, etc.
This goes beyond the basic Company CRUD fields (name, ticker) to create
investment-grade intelligence.
"""

from uuid import UUID

from pydantic import BaseModel, Field


# ── Extraction Schemas (LLM Output Validation) ──


class ExtractedCompanyProfile(BaseModel):
    """
    Structured company profile extracted by GPT-4o.

    Stored in Company.metadata_ JSONB column and used to update
    the Company.industry and Company.description fields.
    """

    business_summary: str = Field(
        description="Comprehensive business description (2–4 paragraphs)"
    )
    industry: str = Field(
        description="Primary industry classification"
    )
    sector: str | None = Field(
        default=None,
        description="Sector classification"
    )
    products: list[str] = Field(
        default_factory=list,
        description="Key products and services"
    )
    business_segments: list[str] = Field(
        default_factory=list,
        description="Business segments or divisions"
    )
    countries: list[str] = Field(
        default_factory=list,
        description="Countries of operation"
    )
    major_customers: list[str] = Field(
        default_factory=list,
        description="Major customers (if disclosed in filings)"
    )
    major_competitors: list[str] = Field(
        default_factory=list,
        description="Major competitors in the same space"
    )
    employee_count: int | None = Field(
        default=None,
        description="Approximate number of employees"
    )
    founded_year: int | None = Field(
        default=None,
        description="Year the company was founded"
    )
    headquarters: str | None = Field(
        default=None,
        description="Headquarters location"
    )


# ── API Schemas ──


class CompanyAnalysisRequest(BaseModel):
    """Request body for POST /api/v1/analysis/company/{company_id}."""

    pass  # company_id comes from the URL path


class CompanyProfileResponse(BaseModel):
    """Response body for company intelligence endpoints."""

    company_id: str
    name: str
    ticker: str | None = None
    business_summary: str | None = None
    industry: str | None = None
    sector: str | None = None
    products: list[str] = Field(default_factory=list)
    business_segments: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)
    major_customers: list[str] = Field(default_factory=list)
    major_competitors: list[str] = Field(default_factory=list)
    employee_count: int | None = None
    founded_year: int | None = None
    headquarters: str | None = None
    status: str = Field(
        default="completed",
        description="Analysis status: completed, partial, no_data"
    )
