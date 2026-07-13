"""
DealOS AI — Search API Endpoint.

Exposes the hybrid retrieval pipeline as a REST API:
    POST /api/v1/search

Follows the same patterns as the existing document and company endpoints:
- Dependency injection via FastAPI's Depends
- Permission-based access control (RUN_ANALYSIS)
- Structured request/response schemas
"""

from fastapi import APIRouter, Depends

from app.api.middleware.auth import CurrentUser
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post(
    "",
    response_model=SearchResponse,
    summary="Search documents using hybrid retrieval",
    responses={
        200: {"description": "Search results with ranked chunks"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid search request"},
    },
)
async def search_documents(
    request: SearchRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.RUN_ANALYSIS)),
):
    """
    Search documents using the hybrid retrieval pipeline.

    Combines BM25 keyword search with pgvector semantic search,
    fuses results using Reciprocal Rank Fusion (RRF), and re-ranks
    using a Cross-Encoder model for maximum precision.

    **Pipeline**: Question → BM25 → Vector Search → RRF → Cross-Encoder → Top Context

    Results are scoped to a single company and include:
    - Retrieved chunk content
    - Similarity scores (from cross-encoder reranking)
    - Source document IDs and page numbers
    - BM25 and vector rank positions for transparency
    """
    service = SearchService(db)
    return await service.search(request)
