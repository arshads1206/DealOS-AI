"""
DealOS AI — Hybrid Retriever (Reciprocal Rank Fusion).

Merges BM25 keyword results and vector semantic results into a single
ranked list using Reciprocal Rank Fusion (RRF).

Why RRF?
- Croft et al. (2009) showed RRF outperforms individual rankers and most
  learned combination methods — without requiring any training data.
- The formula is simple, parameter-free (except k), and robust:
    RRF_score(d) = Σ 1 / (k + rank_i(d))  for each ranking source i
- k=60 is the standard default from the original paper (controls how much
  weight is given to lower-ranked items vs. top-ranked ones).
- Naturally handles different score scales (BM25 scores vs cosine similarity)
  because it only uses rank positions, not raw scores.
"""

import structlog

logger = structlog.get_logger(__name__)

# Default RRF constant from the original paper
DEFAULT_RRF_K = 60


class HybridRetriever:
    """
    Combines multiple retrieval result lists using Reciprocal Rank Fusion.

    Takes ranked results from BM25 and vector search, deduplicates by
    chunk_id, and produces a single merged ranking.
    """

    def __init__(self, rrf_k: int = DEFAULT_RRF_K) -> None:
        """
        Initialize with RRF constant.

        Args:
            rrf_k: The k parameter in the RRF formula. Higher values
                   reduce the influence of high rankings from a single source.
                   Default is 60 (from the original Croft et al. paper).
        """
        self._k = rrf_k

    def fuse(
        self,
        bm25_results: list[dict],
        vector_results: list[dict],
    ) -> list[dict]:
        """
        Fuse BM25 and vector search results using RRF.

        Args:
            bm25_results: Ranked chunks from BM25 (ordered by bm25_score desc).
            vector_results: Ranked chunks from vector search (ordered by similarity desc).

        Returns:
            Merged list of chunk dicts ordered by RRF score descending.
            Each dict is augmented with:
                - ``rrf_score``: The fused relevance score
                - ``bm25_rank``: Rank in BM25 results (None if absent)
                - ``vector_rank``: Rank in vector results (None if absent)
        """
        # Accumulate RRF scores by chunk_id
        rrf_scores: dict[str, float] = {}
        chunk_data: dict[str, dict] = {}
        rank_info: dict[str, dict] = {}

        # Process BM25 results
        for rank, chunk in enumerate(bm25_results, start=1):
            chunk_id = chunk["chunk_id"]
            rrf_score = 1.0 / (self._k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_score
            chunk_data[chunk_id] = chunk
            rank_info.setdefault(chunk_id, {"bm25_rank": None, "vector_rank": None})
            rank_info[chunk_id]["bm25_rank"] = rank

        # Process vector results
        for rank, chunk in enumerate(vector_results, start=1):
            chunk_id = chunk["chunk_id"]
            rrf_score = 1.0 / (self._k + rank)
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + rrf_score
            # Prefer vector chunk data (has similarity score)
            chunk_data[chunk_id] = chunk
            rank_info.setdefault(chunk_id, {"bm25_rank": None, "vector_rank": None})
            rank_info[chunk_id]["vector_rank"] = rank

        # Build merged result list
        merged: list[dict] = []
        for chunk_id, score in rrf_scores.items():
            result = {**chunk_data[chunk_id]}
            result["rrf_score"] = score
            result["bm25_rank"] = rank_info[chunk_id]["bm25_rank"]
            result["vector_rank"] = rank_info[chunk_id]["vector_rank"]
            merged.append(result)

        # Sort by RRF score descending
        merged.sort(key=lambda x: x["rrf_score"], reverse=True)

        logger.info(
            "rrf_fusion_complete",
            bm25_count=len(bm25_results),
            vector_count=len(vector_results),
            merged_count=len(merged),
            top_rrf_score=merged[0]["rrf_score"] if merged else 0.0,
        )

        return merged
