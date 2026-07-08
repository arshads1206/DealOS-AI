"""
DealOS AI — Document Service.

Business logic for document upload, storage, and lifecycle management.
"""

import hashlib
import uuid
from datetime import datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.constants import DocumentStatus
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.audit_repository import AuditLogRepository
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.storage import get_storage

logger = structlog.get_logger(__name__)


class DocumentService:
    """Document upload and lifecycle management."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = DocumentRepository(session)
        self._audit_repo = AuditLogRepository(session)
        self._settings = get_settings()

    async def upload_document(
        self,
        company_id: uuid.UUID,
        uploaded_by: uuid.UUID,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> DocumentUploadResponse:
        """
        Upload a document to storage and create a database record.

        Flow:
        1. Validate file type and size
        2. Generate unique storage path
        3. Upload to object storage (MinIO or local)
        4. Create database record with UPLOADED status
        5. Return upload confirmation (processing happens asynchronously)
        """
        # Validate file extension
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if extension not in self._settings.allowed_extensions:
            raise ValidationError(
                message=f"File type '.{extension}' is not allowed. "
                        f"Allowed: {', '.join(self._settings.allowed_extensions)}",
                error_code="INVALID_FILE_TYPE",
            )

        # Validate file size
        if len(content) > self._settings.max_file_size_bytes:
            raise ValidationError(
                message=f"File size exceeds maximum of {self._settings.max_file_size_mb}MB",
                error_code="FILE_TOO_LARGE",
            )

        # Generate unique storage path
        file_id = uuid.uuid4()
        storage_filename = f"{file_id}.{extension}"
        object_name = f"companies/{company_id}/documents/{storage_filename}"

        # Upload to storage
        storage = get_storage()
        import io
        data_stream = io.BytesIO(content)
        bucket = self._settings.minio_bucket
        storage_path = await storage.upload_file(
            bucket=bucket,
            object_name=object_name,
            data=data_stream,
            content_type=content_type,
            size=len(content),
        )

        # Compute checksum
        checksum = hashlib.sha256(content).hexdigest()

        # Create database record
        document = await self._repo.create(
            filename=storage_filename,
            original_filename=filename,
            content_type=content_type,
            storage_path=storage_path,
            file_size=len(content),
            status=DocumentStatus.UPLOADED,
            company_id=company_id,
            uploaded_by=uploaded_by,
        )

        # Create initial version record
        from app.models.document import DocumentVersion
        version = DocumentVersion(
            version_number=1,
            storage_path=storage_path,
            checksum=checksum,
            file_size=len(content),
            document_id=document.id,
            uploaded_by=uploaded_by,
        )
        self._session.add(version)
        await self._session.flush()

        # Audit log
        await self._audit_repo.create(
            action="document.upload",
            user_id=uploaded_by,
            resource_type="document",
            resource_id=document.id,
            new_values={
                "filename": filename,
                "content_type": content_type,
                "file_size": len(content),
                "company_id": str(company_id),
            },
        )

        logger.info(
            "document_uploaded",
            document_id=str(document.id),
            filename=filename,
            company_id=str(company_id),
        )

        return DocumentUploadResponse(
            id=document.id,
            filename=document.filename,
            original_filename=document.original_filename,
            content_type=document.content_type,
            file_size=document.file_size,
            status=document.status,
            company_id=document.company_id,
        )

    async def get_document(self, document_id: uuid.UUID) -> DocumentResponse:
        """Get a document by ID."""
        document = await self._repo.get_by_id(document_id)
        if document is None:
            raise NotFoundError(resource="Document", resource_id=str(document_id))
        return DocumentResponse.model_validate(document)

    async def list_documents(
        self,
        company_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> tuple[list[DocumentResponse], int]:
        """List documents for a company with optional status filter."""
        documents, total = await self._repo.get_by_company(
            company_id=company_id,
            skip=skip,
            limit=limit,
            status=status,
        )
        return [DocumentResponse.model_validate(d) for d in documents], total

    async def delete_document(
        self,
        document_id: uuid.UUID,
        deleted_by: uuid.UUID,
    ) -> DocumentResponse:
        """Soft-delete a document."""
        document = await self._repo.get_by_id(document_id)
        if document is None:
            raise NotFoundError(resource="Document", resource_id=str(document_id))

        await self._repo.soft_delete(document_id)

        # Audit log
        await self._audit_repo.create(
            action="document.delete",
            user_id=deleted_by,
            resource_type="document",
            resource_id=document_id,
        )

        logger.info("document_deleted", document_id=str(document_id))

        return DocumentResponse.model_validate(document)

    async def get_processing_stats(
        self, company_id: uuid.UUID
    ) -> dict[str, int]:
        """Get document processing statistics for a company."""
        return await self._repo.get_processing_stats(company_id)
