"""
DealOS AI — Abstract Storage Backend.

Defines the interface for file storage operations.
Concrete implementations (MinIO, local filesystem) implement this interface.

Why an abstraction?
- Testability: Tests use LocalStorage instead of needing a running MinIO
- Portability: Swap MinIO for S3, GCS, or Azure Blob without changing business logic
- Clean architecture: Services depend on the interface, not the implementation
"""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: str,
        size: int,
    ) -> str:
        """
        Upload a file to storage.

        Args:
            bucket: Storage bucket/container name.
            object_name: Destination path within the bucket.
            data: File-like object to upload.
            content_type: MIME type of the file.
            size: File size in bytes.

        Returns:
            The storage path (bucket/object_name) for future retrieval.
        """
        ...

    @abstractmethod
    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """
        Download a file from storage.

        Args:
            bucket: Storage bucket/container name.
            object_name: Path within the bucket.

        Returns:
            File contents as bytes.
        """
        ...

    @abstractmethod
    async def delete_file(self, bucket: str, object_name: str) -> None:
        """Delete a file from storage."""
        ...

    @abstractmethod
    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if a file exists in storage."""
        ...

    @abstractmethod
    async def get_presigned_url(
        self, bucket: str, object_name: str, expires_seconds: int = 3600
    ) -> str:
        """
        Generate a pre-signed URL for temporary file access.

        Used for document downloads without exposing storage credentials.
        """
        ...
