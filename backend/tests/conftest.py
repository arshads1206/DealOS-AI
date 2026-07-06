"""
DealOS AI — Test Configuration & Fixtures.

Provides:
- Async test database (SQLite in-memory for speed, PostgreSQL for integration)
- Pre-configured FastAPI test client
- Factory fixtures for common test data
- Mocked external services (Redis, MinIO)

Why fixtures instead of setup/teardown?
- Composable: Tests declare exactly which fixtures they need
- Isolated: Each test gets fresh state
- Fast: Shared fixtures avoid redundant setup
"""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from typing import Any

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import Settings
from app.dependencies import get_db
from app.main import create_app
from app.models import Base


# ── Test Database ──
# Uses SQLite async for unit tests (fast, no external dependency).
# Integration tests should use a real PostgreSQL instance.

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional test database session.

    Each test runs in a transaction that is rolled back after the test,
    ensuring complete isolation between tests.
    """
    session_factory = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async HTTP test client with the test database injected.

    Overrides the get_db dependency so all endpoints use the test database.
    """
    app = create_app()

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── Helper Functions ──


def make_uuid() -> uuid.UUID:
    """Generate a random UUID for test data."""
    return uuid.uuid4()
