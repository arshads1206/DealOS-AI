"""
DealOS AI — MinIO Storage Backend.

S3-compatible object storage for document files.
MinIO runs locally during development and can be replaced with
AWS S3 in production by swapping environment variables.

Why MinIO?
- S3-compatible: Same API works with AWS S3, no code changes
- Free for development: No cloud costs during development
- Docker-native: Runs as a container alongside other services
- Enterprise-ready: Used in production at many organizations
"""

import io
from datetime import timedelta
from typing import BinaryIO

import structlog
from minio import Minio
from minio.error import S3Error

from app.core.exceptions import ExternalServiceError
from app.storage.base import StorageBackend

logger = structlog.get_logger(__name__)


class MinIOStorage(StorageBackend):
    """MinIO/S3-compatible storage implementation."""

    def __init__(self, client: Minio, default_bucket: str = "dealos-documents") -> None:
        self._client = client
        self._default_bucket = default_bucket

    async def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        content_type: str,
        size: int,
    ) -> str:
        """Upload file to MinIO bucket."""
        try:
            # Ensure bucket exists
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)

            self._client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=data,
                length=size,
                content_type=content_type,
            )

            storage_path = f"{bucket}/{object_name}"
            logger.info(
                "file_uploaded",
                bucket=bucket,
                object_name=object_name,
                size=size,
                content_type=content_type,
            )
            return storage_path

        except S3Error as e:
            logger.error("minio_upload_failed", error=str(e))
            raise ExternalServiceError(
                message=f"Failed to upload file: {e}",
                error_code="STORAGE_UPLOAD_FAILED",
            ) from e

    async def download_file(self, bucket: str, object_name: str) -> bytes:
        """Download file from MinIO bucket."""
        try:
            response = self._client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error("minio_download_failed", error=str(e))
            raise ExternalServiceError(
                message=f"Failed to download file: {e}",
                error_code="STORAGE_DOWNLOAD_FAILED",
            ) from e

    async def delete_file(self, bucket: str, object_name: str) -> None:
        """Delete file from MinIO bucket."""
        try:
            self._client.remove_object(bucket, object_name)
            logger.info("file_deleted", bucket=bucket, object_name=object_name)
        except S3Error as e:
            logger.error("minio_delete_failed", error=str(e))
            raise ExternalServiceError(
                message=f"Failed to delete file: {e}",
                error_code="STORAGE_DELETE_FAILED",
            ) from e

    async def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if file exists in MinIO bucket."""
        try:
            self._client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    async def get_presigned_url(
        self, bucket: str, object_name: str, expires_seconds: int = 3600
    ) -> str:
        """Generate pre-signed URL for temporary file access."""
        try:
            url = self._client.presigned_get_object(
                bucket, object_name, expires=timedelta(seconds=expires_seconds)
            )
            return url
        except S3Error as e:
            logger.error("minio_presigned_url_failed", error=str(e))
            raise ExternalServiceError(
                message=f"Failed to generate presigned URL: {e}",
                error_code="STORAGE_URL_FAILED",
            ) from e
