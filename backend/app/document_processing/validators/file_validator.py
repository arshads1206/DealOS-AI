"""
DealOS AI — File Validator.

Validates uploaded files against allowed extensions, MIME types, and size limits.
"""

import structlog

from app.config import get_settings

logger = structlog.get_logger(__name__)

# Map file extensions to expected MIME types
EXTENSION_MIME_MAP: dict[str, list[str]] = {
    "pdf": ["application/pdf"],
    "docx": [
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ],
    "xlsx": [
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ],
    "csv": ["text/csv", "application/csv", "text/plain"],
    "pptx": [
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ],
    "txt": ["text/plain"],
}


class FileValidator:
    """Validate file uploads against configured rules."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def validate(
        self,
        filename: str,
        content_type: str,
        file_size: int,
    ) -> tuple[bool, str | None]:
        """
        Validate a file upload.

        Returns (is_valid, error_message).
        """
        # Extract extension
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

        # Check extension
        if extension not in self._settings.allowed_extensions:
            return False, (
                f"File type '.{extension}' is not allowed. "
                f"Allowed: {', '.join(self._settings.allowed_extensions)}"
            )

        # Check file size
        if file_size > self._settings.max_file_size_bytes:
            return False, (
                f"File size ({file_size / (1024*1024):.1f}MB) exceeds "
                f"maximum of {self._settings.max_file_size_mb}MB"
            )

        # Check MIME type (warn but don't block — browser MIME detection is unreliable)
        expected_mimes = EXTENSION_MIME_MAP.get(extension, [])
        if expected_mimes and content_type not in expected_mimes:
            logger.warning(
                "mime_type_mismatch",
                filename=filename,
                expected=expected_mimes,
                actual=content_type,
            )

        return True, None

    @staticmethod
    def get_extension(filename: str) -> str:
        """Extract file extension from filename."""
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
