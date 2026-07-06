"""
DealOS AI — Local Filesystem Storage Backend.

Fallback storage for development and testing without MinIO.
Files are stored in a local directory with the same interface as MinIO.
"""

import os
from pathlib import Path
from typing import BinaryIO

import structlog

from app.storage.base import StorageBackend

logger = structlog.get_logger(__name__)


class LocalStorage(StorageBackend):
    """Local filesystem storage implementation for development/testing."""

    def __init__(self, base_dir: str = "./storage") -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, bucket: str, object_name: str) -> Path:
        """Construct the full filesystem path."""
        path = self._base_dir / bucket / object_name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: str,
        size: int,
    ) -> str:
        """Write file to local filesystem."""
        path = self._get_path(bucket, object_name)
        with open(path, "wb") as f:
            f.write(data.read())

        storage_path = f"{bucket}/{object_name}"
        logger.info("file_uploaded_locally", path=str(path), size=size)
        return storage_path

    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """Read file from local filesystem."""
        path = self._get_path(bucket, object_name)
        with open(path, "rb") as f:
            return f.read()

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """Delete file from local filesystem."""
        path = self._get_path(bucket, object_name)
        if path.exists():
            os.remove(path)
            logger.info("file_deleted_locally", path=str(path))

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists on local filesystem."""
        path = self._get_path(bucket, object_name)
        return path.exists()

    async def get_presigned_url(
        self, bucket: str, object_name: str, expires_seconds: int = 3600
    ) -> str:
        """Return local file path as URL (not a real presigned URL)."""
        path = self._get_path(bucket, object_name)
        return f"file://{path.absolute()}"
