"""
DealOS AI — BM25 Retriever.

Builds an in-memory BM25Okapi index from document chunks and performs
keyword-based retrieval. The index is built per-query from the chunks
in the database — stateless, no index maintenance required.

Why BM25 alongside vector search?
- BM25 excels at exact keyword matches (company names, ticker symbols, GAAP terms)
- Vector search excels at semantic similarity (paraphrased questions, concept matching)
- Combining both via RRF captures strengths of each approach
- Financial documents contain domain-specific terminology that benefits from lexical matching

The tokenizer is intentionally simple (lowercase + whitespace split) because:
1. Financial text has many numbers and abbreviations that stemming distorts
2. Compound terms like "EBITDA" and "10-K" should remain intact
3. BM25Okapi is robust to tokenization quality — the signal comes from TF-IDF weighting
"""

import re

import structlog
from rank_bm25 import BM25Okapi

from app.core.constants import BM25_TOP_K

logger = structlog.get_logger(__name__)


class BM25Retriever:
    """
    Keyword-based retrieval using BM25 (Okapi variant).

    Builds an ephemeral index from a list of chunk dicts, then scores
    a query against all indexed chunks. Returns ranked results with
    BM25 relevance scores.
    """

    def __init__(self, chunks: list[dict]) -> None:
        """
        Initialize BM25 index from chunk dicts.

        Args:
            chunks: List of chunk dicts, each containing at minimum:
                - chunk_id (str)
                - content (str)
                - document_id (str)
                - chunk_index (int)
                - metadata (dict | None)
                - token_count (int)
        """
        self._chunks = chunks
        self._tokenized_corpus: list[list[str]] = []
        self._index: BM25Okapi | None = None

        self._build_index()

    def _tokenize(self, text: str) -> list[str]:
        """
        Tokenize text for BM25 indexing.

        Uses lowercase + alphanumeric token extraction.
        Preserves numbers and abbreviations important in financial text
        (e.g., "10-K", "EBITDA", "FY2024").
        """
        # Extract alphanumeric tokens, preserving hyphens within words
        tokens = re.findall(r"[a-zA-Z0-9][\w\-]*", text.lower())
        return tokens

    def _build_index(self) -> None:
        """Build BM25 index from the chunk corpus."""
        if not self._chunks:
            logger.warning("bm25_empty_corpus", message="No chunks to index")
            return

        self._tokenized_corpus = [
            self._tokenize(chunk["content"]) for chunk in self._chunks
        ]

        self._index = BM25Okapi(self._tokenized_corpus)

        logger.info(
            "bm25_index_built",
            num_chunks=len(self._chunks),
        )

    def search(self, query: str, top_k: int = BM25_TOP_K) -> list[dict]:
        """
        Search the BM25 index with a query string.

        Args:
            query: The search query.
            top_k: Number of top results to return.

        Returns:
            List of chunk dicts augmented with a ``bm25_score`` key,
            ordered by descending relevance.
        """
        if not self._index or not self._chunks:
            logger.warning("bm25_search_empty", message="No index available")
            return []

        tokenized_query = self._tokenize(query)

        if not tokenized_query:
            logger.warning("bm25_empty_query", query=query)
            return []

        scores = self._index.get_scores(tokenized_query)

        # Pair each chunk with its BM25 score, sort descending
        scored_chunks = [
            {**chunk, "bm25_score": float(score)}
            for chunk, score in zip(self._chunks, scores)
        ]
        scored_chunks.sort(key=lambda x: x["bm25_score"], reverse=True)

        # Filter out zero-score results and limit to top_k
        results = [
            chunk for chunk in scored_chunks[:top_k]
            if chunk["bm25_score"] > 0.0
        ]

        logger.info(
            "bm25_search_complete",
            query_tokens=len(tokenized_query),
            results_returned=len(results),
            top_score=results[0]["bm25_score"] if results else 0.0,
        )

        return results
