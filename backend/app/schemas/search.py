"""
DealOS AI — Search Schemas.

Request/response models for the hybrid search endpoint.
Follows the project's Pydantic schema conventions.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    """Request body for POST /api/v1/search."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The search query in natural language",
        examples=["What are the key risk factors mentioned in the 10-K filing?"],
    )
    company_id: UUID = Field(
        ...,
        description="Company UUID to scope the search to",
    )
    top_k: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of top results to return (1–50)",
    )


class SearchResultItem(BaseModel):
    """A single search result — one retrieved chunk with relevance metadata."""

    chunk_id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document identifier")
    content: str = Field(description="The chunk text content")
    chunk_index: int = Field(description="Chunk position within the document")
    page_number: int | None = Field(
        default=None,
        description="Source page number (if available from parser metadata)",
    )
    similarity_score: float = Field(
        description="Final relevance score after reranking (higher = more relevant)"
    )
    bm25_rank: int | None = Field(
        default=None,
        description="Rank in BM25 keyword results (None if not in BM25 results)",
    )
    vector_rank: int | None = Field(
        default=None,
        description="Rank in vector similarity results (None if not in vector results)",
    )
    metadata: dict | None = Field(
        default=None,
        description="Additional chunk metadata from document parsing",
    )


class SearchResponse(BaseModel):
    """Response body for POST /api/v1/search."""

    results: list[SearchResultItem] = Field(
        description="Ranked search results ordered by relevance"
    )
    total_results: int = Field(
        description="Number of results returned"
    )
    query: str = Field(
        description="The original search query (echoed back for reference)"
    )
    company_id: str = Field(
        description="The company ID the search was scoped to"
    )
