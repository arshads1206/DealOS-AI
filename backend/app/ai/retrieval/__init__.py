"""
DealOS AI — Retrieval Module.

Hybrid retrieval pipeline combining BM25 keyword search,
pgvector semantic search, Reciprocal Rank Fusion, and
Cross-Encoder re-ranking.
"""

from app.ai.retrieval.bm25_retriever import BM25Retriever
from app.ai.retrieval.vector_retriever import VectorRetriever
from app.ai.retrieval.hybrid_retriever import HybridRetriever
from app.ai.retrieval.reranker import CrossEncoderReranker

__all__ = [
    "BM25Retriever",
    "VectorRetriever",
    "HybridRetriever",
    "CrossEncoderReranker",
]
