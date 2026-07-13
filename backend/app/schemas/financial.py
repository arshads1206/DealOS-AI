"""
DealOS AI — Financial Analysis Schemas.

Pydantic models for financial metric extraction, storage, and API responses.

Two categories:
1. Extraction schemas — validate structured output from GPT-4o
2. API schemas — request/response models for the financial analysis endpoints
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ── Extraction Schemas (LLM Output Validation) ──


class ExtractedMetric(BaseModel):
    """
    A single financial metric extracted by GPT-4o.

    This schema validates the LLM's structured JSON output. Each field
    maps directly to a column in the FinancialMetric model.
    """

    metric_name: str = Field(
        description="Standardized metric name (e.g., 'revenue', 'ebitda', 'free_cash_flow')"
    )
    metric_value: float = Field(
        description="Numeric value of the metric"
    )
    currency: str = Field(
        default="USD",
        description="Currency code (ISO 4217)"
    )
    unit: str = Field(
        default="millions",
        description="Unit of measurement: millions, billions, percentage, ratio, absolute"
    )
    period: str = Field(
        description="Reporting period (e.g., 'FY 2023', 'Q1 2024', 'TTM')"
    )
    period_type: str = Field(
        description="Period classification: quarterly, annual, or ttm"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score (0–1)"
    )
    source_text: str | None = Field(
        default=None,
        description="Verbatim text from which the metric was extracted"
    )
    source_page: int | None = Field(
        default=None,
        description="Page number in the source document"
    )


class ExtractionResult(BaseModel):
    """Complete extraction output from the financial extractor."""

    metrics: list[ExtractedMetric] = Field(
        default_factory=list,
        description="List of extracted financial metrics"
    )
    fiscal_year: str | None = Field(
        default=None,
        description="Identified fiscal year (e.g., 'FY 2023')"
    )
    reporting_currency: str = Field(
        default="USD",
        description="Primary reporting currency identified in the document"
    )


# ── API Schemas ──


class FinancialAnalysisRequest(BaseModel):
    """Request body for POST /api/v1/analysis/financial/{company_id}."""

    document_id: UUID | None = Field(
        default=None,
        description="Optional: restrict extraction to a specific document. "
                    "If omitted, extracts from all processed documents.",
    )


class FinancialMetricResponse(BaseModel):
    """A single financial metric returned by the API."""

    id: UUID
    metric_name: str
    metric_value: Decimal
    currency: str | None = None
    unit: str | None = None
    period: str
    period_type: str
    period_start: date | None = None
    period_end: date | None = None
    confidence: Decimal
    source_text: str | None = None
    source_page: int | None = None
    company_id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FinancialAnalysisResponse(BaseModel):
    """Response body for financial analysis endpoints."""

    company_id: str
    metrics: list[FinancialMetricResponse]
    total_metrics: int
    fiscal_year: str | None = None
    reporting_currency: str = "USD"
    status: str = Field(
        default="completed",
        description="Analysis status: completed, partial, no_data"
    )
