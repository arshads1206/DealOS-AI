"""
DealOS AI — Embedding Service.

Generates vector embeddings for text chunks using OpenAI's embedding API.
Supports batched processing with rate limiting.

If no OpenAI API key is configured, falls back to zero vectors
(allows development/testing without an API key).
"""

import structlog
from openai import AsyncOpenAI

from app.config import get_settings
from app.core.constants import EMBEDDING_BATCH_SIZE

logger = structlog.get_logger(__name__)


class EmbeddingService:
    """Generate embeddings for text chunks."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client: AsyncOpenAI | None = None

        if self._settings.openai_api_key:
            self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for a list of texts.

        Processes in batches to respect API rate limits.
        Falls back to zero vectors if no API key is configured.
        """
        if not self._client:
            logger.warning("embedding_fallback", reason="No OpenAI API key configured")
            dimensions = self._settings.openai_embedding_dimensions
            return [[0.0] * dimensions for _ in texts]

        all_embeddings = []

        for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
            batch = texts[i:i + EMBEDDING_BATCH_SIZE]

            try:
                response = await self._client.embeddings.create(
                    model=self._settings.openai_embedding_model,
                    input=batch,
                    dimensions=self._settings.openai_embedding_dimensions,
                )

                batch_embeddings = [
                    item.embedding for item in response.data
                ]
                all_embeddings.extend(batch_embeddings)

                logger.info(
                    "embeddings_generated",
                    batch_start=i,
                    batch_size=len(batch),
                    total_tokens=response.usage.total_tokens,
                )

            except Exception as e:
                logger.error("embedding_error", batch_start=i, error=str(e))
                # Return zero vectors for failed batch
                dimensions = self._settings.openai_embedding_dimensions
                all_embeddings.extend(
                    [[0.0] * dimensions for _ in batch]
                )

        return all_embeddings

    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]
