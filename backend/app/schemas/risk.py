"""
DealOS AI — Risk Analysis Schemas.

Pydantic models for risk extraction, storage, and API responses.

Two categories:
1. Extraction schemas — validate structured output from GPT-4o
2. API schemas — request/response models for the risk analysis endpoints
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


# ── Risk Category Constants ──

RISK_CATEGORIES = [
    "debt_growth",
    "customer_concentration",
    "supplier_concentration",
    "litigation",
    "regulatory",
    "auditor_changes",
    "executive_changes",
    "esg",
    "operational",
    "cybersecurity",
    "market",
    "other",
]


# ── Extraction Schemas (LLM Output Validation) ──


class ExtractedRisk(BaseModel):
    """
    A single risk finding extracted by GPT-4o.

    Maps directly to the RiskFinding model columns.
    """

    risk_category: str = Field(
        description="Risk category from the predefined taxonomy"
    )
    risk_subcategory: str | None = Field(
        default=None,
        description="Optional subcategory for more specific classification"
    )
    title: str = Field(
        description="Short, descriptive title for the risk finding"
    )
    description: str = Field(
        description="Detailed description of the risk"
    )
    severity: str = Field(
        description="Severity level: critical, high, medium, low, or info"
    )
    confidence: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Detection confidence score (0–1)"
    )
    evidence: str = Field(
        description="Verbatim evidence text from the source document"
    )
    reasoning: str | None = Field(
        default=None,
        description="Analytical reasoning explaining why this is a risk"
    )
    source_page: int | None = Field(
        default=None,
        description="Page number in the source document"
    )


class RiskExtractionResult(BaseModel):
    """Complete extraction output from the risk extractor."""

    risks: list[ExtractedRisk] = Field(
        default_factory=list,
        description="List of detected risk findings"
    )


# ── API Schemas ──


class RiskAnalysisRequest(BaseModel):
    """Request body for POST /api/v1/analysis/risk/{company_id}."""

    document_id: UUID | None = Field(
        default=None,
        description="Optional: restrict risk analysis to a specific document. "
                    "If omitted, analyzes all processed documents.",
    )


class RiskFindingResponse(BaseModel):
    """A single risk finding returned by the API."""

    id: UUID
    risk_category: str
    risk_subcategory: str | None = None
    title: str
    description: str
    severity: str
    confidence: Decimal
    evidence: str
    reasoning: str | None = None
    source_page: int | None = None
    metadata: dict | None = Field(default=None, alias="metadata_")
    detected_at: datetime
    company_id: UUID
    document_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class SeveritySummary(BaseModel):
    """Risk count breakdown by severity level."""

    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    info: int = 0


class RiskAnalysisResponse(BaseModel):
    """Response body for risk analysis endpoints."""

    company_id: str
    risks: list[RiskFindingResponse]
    total_risks: int
    severity_summary: SeveritySummary
    status: str = Field(
        default="completed",
        description="Analysis status: completed, partial, no_data"
    )
