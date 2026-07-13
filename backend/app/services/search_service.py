"""
DealOS AI — Search Service.

Orchestrates the full hybrid retrieval pipeline:
    Question → BM25 → Vector Search → RRF Fusion → Cross-Encoder Rerank → Top Context

This service is the single entry point for search operations. It composes
the four retrieval components without duplicating any of their logic.

Pipeline flow:
1. Load all processed chunks for the company from the database
2. Build a BM25 index and run keyword search (in-memory)
3. Embed the query and run pgvector cosine similarity search (in DB)
4. Fuse both result lists using Reciprocal Rank Fusion
5. Re-rank the top candidates using a Cross-Encoder
6. Return structured results with scores and metadata
"""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.retrieval.bm25_retriever import BM25Retriever
from app.ai.retrieval.hybrid_retriever import HybridRetriever
from app.ai.retrieval.reranker import CrossEncoderReranker
from app.ai.retrieval.vector_retriever import VectorRetriever
from app.core.constants import BM25_TOP_K, RERANKER_TOP_K, VECTOR_TOP_K
from app.core.exceptions import NotFoundError, ValidationError
from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.company_repository import CompanyRepository
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem

logger = structlog.get_logger(__name__)


class SearchService:
    """
    Hybrid retrieval pipeline orchestrator.

    Combines BM25 keyword search, pgvector semantic search,
    Reciprocal Rank Fusion, and Cross-Encoder reranking into
    a single search operation.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize with a database session.

        Args:
            session: Async SQLAlchemy session — passed through to
                     repositories and the vector retriever.
        """
        self._session = session
        self._company_repo = CompanyRepository(session)
        self._vector_retriever = VectorRetriever(session)
        self._hybrid_retriever = HybridRetriever()
        self._reranker = CrossEncoderReranker()

    async def search(self, request: SearchRequest) -> SearchResponse:
        """
        Execute the full hybrid retrieval pipeline.

        Args:
            request: Validated search request with question, company_id, top_k.

        Returns:
            SearchResponse with ranked chunks, scores, and metadata.

        Raises:
            NotFoundError: If the company does not exist.
            ValidationError: If no processed documents exist for the company.
        """
        logger.info(
            "search_pipeline_start",
            question_preview=request.question[:100],
            company_id=str(request.company_id),
            top_k=request.top_k,
        )

        # ── Step 0: Validate company exists ──
        company = await self._company_repo.get_by_id(request.company_id)
        if company is None:
            raise NotFoundError(
                resource="Company",
                resource_id=str(request.company_id),
            )

        # ── Step 1: Load all chunks for the company ──
        chunks_for_bm25 = await self._load_company_chunks(request.company_id)

        if not chunks_for_bm25:
            logger.warning(
                "search_no_chunks",
                company_id=str(request.company_id),
            )
            return SearchResponse(
                results=[],
                total_results=0,
                query=request.question,
                company_id=str(request.company_id),
            )

        # ── Step 2: BM25 keyword search ──
        bm25_retriever = BM25Retriever(chunks_for_bm25)
        bm25_results = bm25_retriever.search(
            query=request.question,
            top_k=BM25_TOP_K,
        )

        logger.info(
            "search_bm25_done",
            bm25_results=len(bm25_results),
        )

        # ── Step 3: Vector semantic search ──
        vector_results = await self._vector_retriever.search(
            query=request.question,
            company_id=request.company_id,
            top_k=VECTOR_TOP_K,
        )

        logger.info(
            "search_vector_done",
            vector_results=len(vector_results),
        )

        # ── Step 4: Reciprocal Rank Fusion ──
        fused_results = self._hybrid_retriever.fuse(
            bm25_results=bm25_results,
            vector_results=vector_results,
        )

        logger.info(
            "search_rrf_done",
            fused_results=len(fused_results),
        )

        # ── Step 5: Cross-Encoder reranking ──
        # Rerank the top candidates (limit input to avoid excessive inference)
        candidates_for_rerank = fused_results[:max(request.top_k * 3, RERANKER_TOP_K)]
        reranked_results = self._reranker.rerank(
            query=request.question,
            chunks=candidates_for_rerank,
            top_k=request.top_k,
        )

        logger.info(
            "search_rerank_done",
            reranked_results=len(reranked_results),
        )

        # ── Step 6: Format response ──
        result_items = [
            self._format_result(chunk) for chunk in reranked_results
        ]

        logger.info(
            "search_pipeline_complete",
            total_results=len(result_items),
            company_id=str(request.company_id),
        )

        return SearchResponse(
            results=result_items,
            total_results=len(result_items),
            query=request.question,
            company_id=str(request.company_id),
        )

    async def _load_company_chunks(self, company_id: UUID) -> list[dict]:
        """
        Load all chunks belonging to processed documents for a company.

        Returns chunk dicts in the format expected by BM25Retriever.
        Only includes chunks from documents with status='processed'.
        """
        stmt = (
            select(
                Chunk.id,
                Chunk.chunk_index,
                Chunk.content,
                Chunk.token_count,
                Chunk.metadata_,
                Chunk.document_id,
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(
                Document.company_id == company_id,
                Document.is_deleted == False,  # noqa: E712
                Document.status == "processed",
            )
            .order_by(Chunk.document_id, Chunk.chunk_index)
        )

        result = await self._session.execute(stmt)
        rows = result.all()

        return [
            {
                "chunk_id": str(row.id),
                "chunk_index": row.chunk_index,
                "content": row.content,
                "token_count": row.token_count,
                "metadata": row.metadata_ if row.metadata_ else {},
                "document_id": str(row.document_id),
            }
            for row in rows
        ]

    @staticmethod
    def _format_result(chunk: dict) -> SearchResultItem:
        """
        Format a raw chunk dict into a SearchResultItem response model.

        Extracts page_number from chunk metadata if available.
        Uses rerank_score as the primary similarity_score.
        """
        metadata = chunk.get("metadata", {}) or {}

        # Page number may be stored in metadata by the document parsers
        page_number = metadata.get("page_number") or metadata.get("page")

        return SearchResultItem(
            chunk_id=chunk["chunk_id"],
            document_id=chunk["document_id"],
            content=chunk["content"],
            chunk_index=chunk["chunk_index"],
            page_number=int(page_number) if page_number is not None else None,
            similarity_score=chunk.get("rerank_score", chunk.get("rrf_score", 0.0)),
            bm25_rank=chunk.get("bm25_rank"),
            vector_rank=chunk.get("vector_rank"),
            metadata=metadata,
        )
