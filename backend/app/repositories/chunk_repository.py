"""
DealOS AI — Chunk Repository.

Data access layer for chunk storage and vector similarity search.
Uses pgvector for native cosine similarity queries.
"""

from uuid import UUID

from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.repositories.base import CRUDRepository


class ChunkRepository(CRUDRepository[Chunk]):
    """Chunk-specific data access methods with vector search."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Chunk, session)

    async def create_bulk(self, chunks: list[dict]) -> list[Chunk]:
        """
        Bulk insert chunks for a document.

        Args:
            chunks: List of chunk dicts with keys:
                chunk_index, content, embedding, metadata_, token_count, document_id
        """
        chunk_objects = [Chunk(**chunk_data) for chunk_data in chunks]
        self._session.add_all(chunk_objects)
        await self._session.flush()
        return chunk_objects

    async def delete_by_document(self, document_id: UUID) -> int:
        """Delete all chunks for a document (used during reprocessing)."""
        stmt = delete(Chunk).where(Chunk.document_id == document_id)
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.rowcount

    async def get_by_document(
        self,
        document_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Chunk]:
        """Get chunks for a document ordered by chunk_index."""
        stmt = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def vector_search(
        self,
        query_embedding: list[float],
        company_id: UUID | None = None,
        document_id: UUID | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """
        Perform cosine similarity search using pgvector.

        Args:
            query_embedding: The query vector.
            company_id: Optional filter by company.
            document_id: Optional filter by document.
            top_k: Number of results to return.

        Returns:
            List of dicts with chunk data and similarity score.
        """
        # Build the query with pgvector cosine distance operator
        # cosine_distance = 1 - cosine_similarity
        # So we order by distance ASC (smaller distance = more similar)
        embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

        filters = []
        if document_id:
            filters.append(f"c.document_id = '{document_id}'")
        if company_id:
            filters.append(f"d.company_id = '{company_id}'")

        where_clause = ""
        if filters:
            where_clause = "WHERE " + " AND ".join(filters)

        # Use raw SQL for pgvector operations
        query = text(f"""
            SELECT
                c.id,
                c.chunk_index,
                c.content,
                c.token_count,
                c.metadata,
                c.document_id,
                1 - (c.embedding <=> :embedding::vector) AS similarity
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            {where_clause}
            ORDER BY c.embedding <=> :embedding::vector
            LIMIT :top_k
        """)

        result = await self._session.execute(
            query,
            {"embedding": embedding_str, "top_k": top_k},
        )

        rows = result.fetchall()
        return [
            {
                "chunk_id": str(row.id),
                "chunk_index": row.chunk_index,
                "content": row.content,
                "token_count": row.token_count,
                "metadata": row.metadata,
                "document_id": str(row.document_id),
                "similarity": float(row.similarity),
            }
            for row in rows
        ]

    async def count_by_document(self, document_id: UUID) -> int:
        """Count chunks for a document."""
        stmt = (
            select(func.count())
            .select_from(Chunk)
            .where(Chunk.document_id == document_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
