"""
DealOS AI — Document Schemas.

Pydantic models for document upload, listing, and status tracking.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Document data returned to clients."""

    id: UUID
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    status: str
    error_message: str | None = None
    current_version: int
    company_id: UUID
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    """Response after a successful document upload."""

    id: UUID
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    status: str
    company_id: UUID
    message: str = "Document uploaded successfully. Processing will begin shortly."

    model_config = {"from_attributes": True}


class DocumentVersionResponse(BaseModel):
    """Document version history entry."""

    id: UUID
    version_number: int
    file_size: int
    checksum: str
    uploaded_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentWithChunks(DocumentResponse):
    """Document with chunk count for detail views."""

    chunk_count: int = 0
    version_count: int = 0
