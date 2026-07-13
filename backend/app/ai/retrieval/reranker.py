"""
DealOS AI — Cross-Encoder Reranker.

Re-ranks retrieved chunks using a Cross-Encoder model that jointly encodes
the (query, passage) pair for high-precision relevance scoring.

Why a Cross-Encoder on top of BM25 + vector search?
- Bi-encoders (used for vector search) encode query and passage independently,
  missing fine-grained token interactions between them.
- Cross-Encoders attend to both query and passage simultaneously, capturing
  nuanced relevance signals (negation, conditional statements, entity overlap).
- The cost is O(n) model inferences, so we apply it only to the top candidates
  after the fast first-stage retrievers narrow the field.

Model choice: cross-encoder/ms-marco-MiniLM-L-6-v2
- 22MB, 6-layer MiniLM — fast enough for real-time reranking of ~50 candidates
- Trained on MS MARCO passage ranking — strong zero-shot performance on financial text
- sentence-transformers CrossEncoder API handles tokenization and batching
"""

from functools import lru_cache

import structlog
from sentence_transformers import CrossEncoder

from app.core.constants import RERANKER_TOP_K

logger = structlog.get_logger(__name__)

# Model identifier — small, fast, high-quality reranker
CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def _load_cross_encoder() -> CrossEncoder:
    """
    Load the Cross-Encoder model (singleton via lru_cache).

    The model is loaded lazily on first use and cached for the process
    lifetime. This avoids:
    - Startup latency: The model isn't loaded until search is first called
    - Memory waste: Only loaded if the search feature is actually used
    - Repeated loads: Cached across all requests in the same worker
    """
    logger.info("cross_encoder_loading", model=CROSS_ENCODER_MODEL)
    model = CrossEncoder(CROSS_ENCODER_MODEL)
    logger.info("cross_encoder_loaded", model=CROSS_ENCODER_MODEL)
    return model


class CrossEncoderReranker:
    """
    Re-rank retrieved chunks using a Cross-Encoder for precision.

    Takes the merged results from HybridRetriever and re-scores each
    (query, chunk_content) pair using cross-attention, then returns
    the top-k most relevant chunks.
    """

    def __init__(self) -> None:
        """Initialize reranker (model is loaded lazily on first use)."""
        self._model: CrossEncoder | None = None

    def _get_model(self) -> CrossEncoder:
        """Get or load the Cross-Encoder model."""
        if self._model is None:
            self._model = _load_cross_encoder()
        return self._model

    def rerank(
        self,
        query: str,
        chunks: list[dict],
        top_k: int = RERANKER_TOP_K,
    ) -> list[dict]:
        """
        Re-rank chunks using the Cross-Encoder.

        Args:
            query: The original search query.
            chunks: List of chunk dicts from HybridRetriever (with rrf_score).
            top_k: Number of top results to return after reranking.

        Returns:
            List of chunk dicts ordered by cross-encoder score descending,
            augmented with a ``rerank_score`` key.
        """
        if not chunks:
            return []

        model = self._get_model()

        # Build (query, passage) pairs for cross-encoder scoring
        sentence_pairs = [
            [query, chunk["content"]] for chunk in chunks
        ]

        logger.info(
            "reranking_start",
            num_candidates=len(chunks),
            top_k=top_k,
        )

        # Score all pairs in a single batch
        scores = model.predict(sentence_pairs)

        # Augment chunks with rerank scores
        reranked = [
            {**chunk, "rerank_score": float(score)}
            for chunk, score in zip(chunks, scores)
        ]

        # Sort by cross-encoder score descending and take top_k
        reranked.sort(key=lambda x: x["rerank_score"], reverse=True)
        results = reranked[:top_k]

        logger.info(
            "reranking_complete",
            results_returned=len(results),
            top_rerank_score=results[0]["rerank_score"] if results else 0.0,
        )

        return results
