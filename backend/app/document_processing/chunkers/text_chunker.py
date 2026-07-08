"""
DealOS AI — Text Chunker.

Splits parsed document text into semantically meaningful chunks
for embedding and retrieval.

Chunking strategy:
- Recursive character splitting with paragraph/sentence awareness
- Configurable chunk size and overlap
- Token counting via tiktoken for accurate LLM context management
- Metadata preservation (page number, chunk index)
"""

import re

import structlog
import tiktoken

from app.core.constants import MAX_CHUNKS_PER_DOCUMENT

logger = structlog.get_logger(__name__)

# Default chunking parameters
DEFAULT_CHUNK_SIZE = 1000  # target tokens per chunk
DEFAULT_CHUNK_OVERLAP = 150  # overlap tokens between chunks
ENCODING_NAME = "cl100k_base"  # GPT-4/text-embedding-3 tokenizer


class TextChunker:
    """Split text into overlapping chunks with token counting."""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._encoding = tiktoken.get_encoding(ENCODING_NAME)

    def chunk_pages(self, pages: list[dict]) -> list[dict]:
        """
        Chunk parsed document pages into embedding-ready chunks.

        Args:
            pages: List of page dicts from parsers (page_number, text, metadata).

        Returns:
            List of chunk dicts with: chunk_index, content, token_count, metadata.
        """
        chunks = []
        chunk_index = 0

        for page in pages:
            page_text = page["text"]
            page_number = page["page_number"]
            page_metadata = page.get("metadata", {})

            # Split page text into paragraphs
            paragraphs = self._split_into_paragraphs(page_text)

            current_chunk = ""
            current_tokens = 0

            for paragraph in paragraphs:
                para_tokens = self._count_tokens(paragraph)

                # If a single paragraph exceeds chunk_size, split it further
                if para_tokens > self._chunk_size:
                    # Flush current chunk first
                    if current_chunk.strip():
                        chunks.append(self._make_chunk(
                            chunk_index, current_chunk.strip(),
                            page_number, page_metadata,
                        ))
                        chunk_index += 1

                    # Split large paragraph by sentences
                    sub_chunks = self._split_large_text(paragraph)
                    for sub_chunk in sub_chunks:
                        chunks.append(self._make_chunk(
                            chunk_index, sub_chunk,
                            page_number, page_metadata,
                        ))
                        chunk_index += 1

                    current_chunk = ""
                    current_tokens = 0
                    continue

                # Check if adding this paragraph exceeds chunk_size
                if current_tokens + para_tokens > self._chunk_size:
                    # Flush current chunk
                    if current_chunk.strip():
                        chunks.append(self._make_chunk(
                            chunk_index, current_chunk.strip(),
                            page_number, page_metadata,
                        ))
                        chunk_index += 1

                    # Start new chunk with overlap from previous
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = overlap_text + paragraph + "\n\n"
                    current_tokens = self._count_tokens(current_chunk)
                else:
                    current_chunk += paragraph + "\n\n"
                    current_tokens += para_tokens

            # Flush remaining text
            if current_chunk.strip():
                chunks.append(self._make_chunk(
                    chunk_index, current_chunk.strip(),
                    page_number, page_metadata,
                ))
                chunk_index += 1

        # Safety: limit total chunks
        if len(chunks) > MAX_CHUNKS_PER_DOCUMENT:
            logger.warning(
                "chunks_truncated",
                total=len(chunks),
                limit=MAX_CHUNKS_PER_DOCUMENT,
            )
            chunks = chunks[:MAX_CHUNKS_PER_DOCUMENT]

        logger.info("text_chunked", total_chunks=len(chunks))
        return chunks

    def _make_chunk(
        self,
        index: int,
        content: str,
        page_number: int,
        page_metadata: dict,
    ) -> dict:
        """Create a chunk dict with metadata."""
        return {
            "chunk_index": index,
            "content": content,
            "token_count": self._count_tokens(content),
            "metadata": {
                "page_number": page_number,
                **page_metadata,
            },
        }

    def _count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        return len(self._encoding.encode(text))

    def _split_into_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs by double newlines."""
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _split_large_text(self, text: str) -> list[str]:
        """Split a large text block by sentences when it exceeds chunk_size."""
        sentences = re.split(r"(?<=[.!?])\s+", text)
        chunks = []
        current = ""
        current_tokens = 0

        for sentence in sentences:
            sent_tokens = self._count_tokens(sentence)
            if current_tokens + sent_tokens > self._chunk_size and current:
                chunks.append(current.strip())
                current = ""
                current_tokens = 0
            current += sentence + " "
            current_tokens += sent_tokens

        if current.strip():
            chunks.append(current.strip())

        return chunks

    def _get_overlap(self, text: str) -> str:
        """Get the trailing overlap from the previous chunk."""
        if not text:
            return ""
        tokens = self._encoding.encode(text)
        if len(tokens) <= self._chunk_overlap:
            return text
        overlap_tokens = tokens[-self._chunk_overlap:]
        return self._encoding.decode(overlap_tokens)
