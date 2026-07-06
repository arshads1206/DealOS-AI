"""
DealOS AI — Dependency Injection.

FastAPI's dependency injection system provides request-scoped resources
(database sessions, Redis connections, storage clients) to endpoint handlers.

Why DI instead of global singletons?
- Testability: Tests can inject mock dependencies
- Lifecycle management: Sessions are created per-request and properly closed
- Explicit dependencies: Each endpoint declares what it needs
- Connection pooling: SQLAlchemy's pool is managed at the engine level
"""

from collections.abc import AsyncGenerator
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from minio import Minio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings, get_settings

# ── Database Engine (Module-Level Singleton) ──
# Created once at import time, reused across all requests.
# SQLAlchemy manages its own connection pool internally.

_engine = None
_async_session_factory = None


def _get_engine(settings: Settings | None = None):
    """Lazily create the async engine."""
    global _engine
    if _engine is None:
        if settings is None:
            settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,  # Detect stale connections
            pool_recycle=3600,   # Recycle connections after 1 hour
        )
    return _engine


def _get_session_factory(settings: Settings | None = None) -> async_sessionmaker[AsyncSession]:
    """Lazily create the session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        engine = _get_engine(settings)
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Prevent lazy-load issues after commit
        )
    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a request-scoped async database session.

    Usage:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...

    The session is committed on success and rolled back on error.
    """
    session_factory = _get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """
    Provide a request-scoped Redis connection.

    Used for: rate limiting, session cache, BM25 index storage, job queue.
    """
    settings = get_settings()
    client = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        yield client
    finally:
        await client.aclose()


def get_minio_client() -> Minio:
    """
    Provide a MinIO client for object storage operations.

    MinIO client is thread-safe and can be reused across requests.
    """
    settings = get_settings()
    return Minio(
        endpoint=settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=settings.minio_use_ssl,
    )


# ── Type Aliases for Clean Endpoint Signatures ──

DbSession = Annotated[AsyncSession, Depends(get_db)]
RedisClient = Annotated[aioredis.Redis, Depends(get_redis)]
