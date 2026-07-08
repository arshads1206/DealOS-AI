"""
DealOS AI — Company Schemas.

Pydantic models for company CRUD operations.

Key schemas:
- CompanyCreate: Creating a new company workspace
- CompanyUpdate: Partial updates (name, industry, etc.)
- CompanyResponse: Public-facing company data with computed stats
- CompanySummary: Lightweight version for list views
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """Create a new company workspace."""

    name: str = Field(min_length=1, max_length=255, description="Company name")
    ticker: str | None = Field(default=None, max_length=20, description="Stock ticker symbol")
    industry: str | None = Field(default=None, max_length=255, description="Industry classification")
    sector: str | None = Field(default=None, max_length=255, description="Sector classification")
    description: str | None = Field(default=None, description="Company description")
    country: str | None = Field(default=None, max_length=100, description="Country of incorporation")
    metadata: dict | None = Field(default=None, description="Additional metadata")


class CompanyUpdate(BaseModel):
    """Partial company update. Only provided fields are updated."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    ticker: str | None = Field(default=None, max_length=20)
    industry: str | None = Field(default=None, max_length=255)
    sector: str | None = Field(default=None, max_length=255)
    description: str | None = None
    country: str | None = Field(default=None, max_length=100)
    metadata: dict | None = None


class CompanyResponse(BaseModel):
    """Company data returned to clients."""

    id: UUID
    name: str
    ticker: str | None = None
    industry: str | None = None
    sector: str | None = None
    description: str | None = None
    country: str | None = None
    metadata: dict | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyWithStats(CompanyResponse):
    """Company with aggregated statistics for detail views."""

    document_count: int = 0
    processed_document_count: int = 0
    risk_finding_count: int = 0
    report_count: int = 0

    model_config = {"from_attributes": True}
