"""Storage backends package."""

from app.storage.base import StorageBackend
from app.storage.minio_storage import MinIOStorage
from app.storage.local_storage import LocalStorage


def get_storage() -> LocalStorage:
    """
    Get the configured storage backend.

    Returns LocalStorage for development (no MinIO dependency required).
    In production (Docker), this would return MinIOStorage.
    """
    return LocalStorage()


__all__ = ["StorageBackend", "MinIOStorage", "LocalStorage", "get_storage"]
