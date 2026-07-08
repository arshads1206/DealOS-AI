"""
DealOS AI — Document Management Endpoints.

REST API for document upload and management:
- POST /companies/{id}/documents — Upload a document
- GET /companies/{id}/documents — List documents for a company
- GET /documents/{id} — Get document details
- DELETE /documents/{id} — Soft delete a document
"""

import uuid

from fastapi import APIRouter, Depends, Query, UploadFile, File

from app.api.middleware.auth import CurrentUser
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.common import PaginatedResponse, PaginationMeta
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter()


@router.post(
    "/companies/{company_id}/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    summary="Upload a document to a company workspace",
    responses={
        201: {"description": "Document uploaded successfully"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid file type or size"},
    },
)
async def upload_document(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    file: UploadFile = File(..., description="Document file to upload"),
    _: None = Depends(PermissionChecker(Permission.UPLOAD_DOCUMENTS)),
):
    """
    Upload a document to a company workspace.

    Supported formats: PDF, DOCX, XLSX, CSV, PPTX, TXT.
    Maximum file size: 50MB (configurable).

    The document is stored immediately and processing
    (parsing, chunking, embedding) happens asynchronously.
    """
    content = await file.read()
    service = DocumentService(db)
    return await service.upload_document(
        company_id=company_id,
        uploaded_by=uuid.UUID(current_user["user_id"]),
        filename=file.filename or "unnamed",
        content=content,
        content_type=file.content_type or "application/octet-stream",
    )


@router.get(
    "/companies/{company_id}/list",
    response_model=PaginatedResponse[DocumentResponse],
    summary="List documents for a company",
    responses={
        200: {"description": "Paginated document list"},
    },
)
async def list_documents(
    company_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DOCUMENTS)),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(default=None, description="Filter by status"),
):
    """
    List all documents in a company workspace.

    Optionally filter by processing status: uploaded, processing, processed, failed.
    """
    service = DocumentService(db)
    skip = (page - 1) * page_size
    documents, total = await service.list_documents(
        company_id=company_id,
        skip=skip,
        limit=page_size,
        status=status,
    )

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        data=documents,
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
    responses={
        200: {"description": "Document details with processing status"},
        404: {"description": "Document not found"},
    },
)
async def get_document(
    document_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.VIEW_DOCUMENTS)),
):
    """Get detailed information about a specific document."""
    service = DocumentService(db)
    return await service.get_document(document_id)


@router.delete(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Delete document (soft delete)",
    responses={
        200: {"description": "Document deleted"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Document not found"},
    },
)
async def delete_document(
    document_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.DELETE_RESOURCES)),
):
    """
    Soft-delete a document.

    The document and its chunks are preserved but hidden from queries.
    Requires `delete_resources` permission (admin only).
    """
    service = DocumentService(db)
    return await service.delete_document(
        document_id=document_id,
        deleted_by=uuid.UUID(current_user["user_id"]),
    )
