"""
DealOS AI — Document Processing Service.

Orchestrates the full document processing pipeline:
parse → chunk → embed → store

This service coordinates between parsers, chunkers, embedding service,
and repositories to transform a raw uploaded document into searchable chunks.
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.embedding_service import EmbeddingService
from app.core.constants import DocumentStatus
from app.core.exceptions import FileProcessingError
from app.document_processing.chunkers.text_chunker import TextChunker
from app.document_processing.parsers.docx_parser import DocxParser
from app.document_processing.parsers.excel_parser import ExcelParser
from app.document_processing.parsers.pdf_parser import PDFParser
from app.document_processing.parsers.pptx_parser import PptxParser
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.storage import get_storage

logger = structlog.get_logger(__name__)

# Map file extensions to their parsers
PARSER_MAP = {
    "pdf": PDFParser,
    "docx": DocxParser,
    "pptx": PptxParser,
    "xlsx": ExcelParser,
    "csv": ExcelParser,
    "txt": None,  # Handled inline
}


class ProcessingService:
    """Orchestrate document processing pipeline."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._doc_repo = DocumentRepository(session)
        self._chunk_repo = ChunkRepository(session)
        self._chunker = TextChunker()
        self._embedding_service = EmbeddingService()

    async def process_document(self, document_id) -> None:
        """
        Full processing pipeline for a document.

        Steps:
        1. Update status to PROCESSING
        2. Download file from storage
        3. Parse to extract text by page
        4. Chunk text into embedding-sized pieces
        5. Generate embeddings for each chunk
        6. Store chunks with embeddings in database
        7. Update status to PROCESSED (or FAILED on error)
        """
        import uuid
        doc_id = uuid.UUID(str(document_id))

        # Get document
        document = await self._doc_repo.get_by_id(doc_id)
        if document is None:
            logger.error("document_not_found", document_id=str(doc_id))
            return

        # Update status to processing
        await self._doc_repo.update_status(doc_id, DocumentStatus.PROCESSING)
        await self._session.commit()

        try:
            # Step 1: Download file from storage
            storage = get_storage()
            bucket_and_path = document.storage_path.split("/", 1)
            if len(bucket_and_path) == 2:
                bucket, object_name = bucket_and_path
            else:
                bucket = "dealos-documents"
                object_name = document.storage_path

            content = await storage.download_file(bucket, object_name)

            # Step 2: Parse document
            extension = document.original_filename.rsplit(".", 1)[-1].lower()
            pages = await self._parse_document(content, extension, document.original_filename)

            if not pages:
                raise FileProcessingError(
                    message="No text content extracted from document",
                    error_code="EMPTY_DOCUMENT",
                )

            # Step 3: Chunk text
            chunks = self._chunker.chunk_pages(pages)

            logger.info(
                "document_chunked",
                document_id=str(doc_id),
                total_chunks=len(chunks),
            )

            # Step 4: Generate embeddings
            texts = [chunk["content"] for chunk in chunks]
            embeddings = await self._embedding_service.embed_texts(texts)

            # Step 5: Delete existing chunks (for reprocessing)
            await self._chunk_repo.delete_by_document(doc_id)

            # Step 6: Store chunks with embeddings
            chunk_records = []
            for chunk, embedding in zip(chunks, embeddings):
                chunk_records.append({
                    "chunk_index": chunk["chunk_index"],
                    "content": chunk["content"],
                    "embedding": embedding,
                    "metadata_": chunk["metadata"],
                    "token_count": chunk["token_count"],
                    "document_id": doc_id,
                })

            await self._chunk_repo.create_bulk(chunk_records)

            # Step 7: Update status to processed
            await self._doc_repo.update_status(doc_id, DocumentStatus.PROCESSED)
            await self._session.commit()

            logger.info(
                "document_processed",
                document_id=str(doc_id),
                chunks=len(chunks),
            )

        except Exception as e:
            logger.error(
                "document_processing_failed",
                document_id=str(doc_id),
                error=str(e),
            )
            await self._session.rollback()
            await self._doc_repo.update_status(
                doc_id, DocumentStatus.FAILED, error_message=str(e)
            )
            await self._session.commit()

    async def _parse_document(
        self,
        content: bytes,
        extension: str,
        filename: str,
    ) -> list[dict]:
        """Parse a document using the appropriate parser."""
        if extension == "txt":
            text = content.decode("utf-8", errors="replace")
            return [{"page_number": 1, "text": text, "metadata": {"source_type": "txt"}}]

        if extension == "pdf":
            return await PDFParser.parse(content)

        if extension == "docx":
            return await DocxParser.parse(content)

        if extension in ("xlsx", "csv"):
            return await ExcelParser.parse(content, filename)

        if extension == "pptx":
            return await PptxParser.parse(content)

        raise FileProcessingError(
            message=f"Unsupported file type: .{extension}",
            error_code="UNSUPPORTED_FILE_TYPE",
        )
