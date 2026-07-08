"""
DealOS AI — PDF Parser.

Extracts text from PDF files using PyMuPDF (fitz).
Preserves page boundaries for citation tracking.
"""

import structlog
import fitz  # PyMuPDF

logger = structlog.get_logger(__name__)


class PDFParser:
    """Extract text content from PDF documents."""

    @staticmethod
    async def parse(content: bytes) -> list[dict]:
        """
        Parse a PDF file and extract text by page.

        Args:
            content: Raw PDF file bytes.

        Returns:
            List of dicts with keys: page_number, text, metadata.
        """
        pages = []

        try:
            doc = fitz.open(stream=content, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                if text.strip():
                    pages.append({
                        "page_number": page_num + 1,
                        "text": text.strip(),
                        "metadata": {
                            "width": page.rect.width,
                            "height": page.rect.height,
                            "rotation": page.rotation,
                        },
                    })

            doc.close()

            logger.info("pdf_parsed", total_pages=len(doc), pages_with_text=len(pages))

        except Exception as e:
            logger.error("pdf_parse_error", error=str(e))
            raise

        return pages
