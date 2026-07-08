"""
DealOS AI — Background Document Processor.

Entry point for asynchronous document processing.
Triggered after a document upload, runs the full processing pipeline
in the background without blocking the API response.
"""

import asyncio

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import _get_session_factory
from app.services.processing_service import ProcessingService

logger = structlog.get_logger(__name__)


async def process_document_background(document_id: str) -> None:
    """
    Process a document in the background.

    Creates its own database session since background tasks
    run outside the request lifecycle.
    """
    session_factory = _get_session_factory()

    async with session_factory() as session:
        try:
            service = ProcessingService(session)
            await service.process_document(document_id)
            logger.info("background_processing_complete", document_id=document_id)
        except Exception as e:
            logger.error(
                "background_processing_error",
                document_id=document_id,
                error=str(e),
            )


def trigger_processing(document_id: str) -> None:
    """
    Trigger document processing as a background task.

    This is called from the document upload endpoint via FastAPI's
    BackgroundTasks to avoid blocking the response.
    """
    asyncio.create_task(process_document_background(document_id))
