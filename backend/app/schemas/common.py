"""
DealOS AI — Common Pydantic Schemas.

Reusable response shapes used across all endpoints.
These enforce a consistent API contract.
"""

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Standard error response body."""

    code: str = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error message")
    details: dict = Field(default_factory=dict, description="Additional context")


class ErrorResponse(BaseModel):
    """Wrapper for error responses."""

    error: ErrorDetail


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    total: int = Field(description="Total number of records")
    page: int = Field(description="Current page number (1-indexed)")
    page_size: int = Field(description="Number of records per page")
    total_pages: int = Field(description="Total number of pages")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    data: list[T]
    meta: PaginationMeta


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str | None = None


class MessageResponse(BaseModel):
    """Simple message response for operations without a return body."""

    message: str


class TimestampMixin(BaseModel):
    """Mixin for responses that include timestamps."""

    created_at: datetime
    updated_at: datetime
