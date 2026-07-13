"""
DealOS AI — Vector Retriever.

Performs semantic similarity search using pgvector's cosine distance operator.
Delegates embedding generation to EmbeddingService and vector search to
ChunkRepository — no duplicated logic.

Why a separate class instead of calling ChunkRepository directly?
- Single Responsibility: VectorRetriever owns "embed query → search vectors → format results"
- The service layer shouldn't know about embedding + search orchestration
- Testable: Mock VectorRetriever in SearchService tests without mocking two dependencies
"""

from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings.embedding_service import EmbeddingService
from app.core.constants import VECTOR_TOP_K
from app.repositories.chunk_repository import ChunkRepository

logger = structlog.get_logger(__name__)


class VectorRetriever:
    """
    Semantic retrieval using OpenAI embeddings + pgvector cosine similarity.

    Wraps the existing EmbeddingService and ChunkRepository to provide
    a clean retrieval interface.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize with a database session.

        Args:
            session: Async SQLAlchemy session for chunk queries.
        """
        self._chunk_repo = ChunkRepository(session)
        self._embedding_service = EmbeddingService()

    async def search(
        self,
        query: str,
        company_id: UUID | None = None,
        document_id: UUID | None = None,
        top_k: int = VECTOR_TOP_K,
    ) -> list[dict]:
        """
        Embed a query and perform cosine similarity search.

        Args:
            query: The search query in natural language.
            company_id: Optional filter — restrict results to a company.
            document_id: Optional filter — restrict results to a document.
            top_k: Number of top results to return.

        Returns:
            List of chunk dicts with ``similarity`` score (0–1, higher = more similar).
        """
        logger.info(
            "vector_search_start",
            query_preview=query[:100],
            company_id=str(company_id) if company_id else None,
            top_k=top_k,
        )

        # Step 1: Embed the query using the same model that embedded the chunks
        query_embedding = await self._embedding_service.embed_single(query)

        # Step 2: Run pgvector cosine similarity search via existing repository
        results = await self._chunk_repo.vector_search(
            query_embedding=query_embedding,
            company_id=company_id,
            document_id=document_id,
            top_k=top_k,
        )

        logger.info(
            "vector_search_complete",
            results_returned=len(results),
            top_similarity=results[0]["similarity"] if results else 0.0,
        )

        return results
