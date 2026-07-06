"""
DealOS AI — FastAPI Application Factory.

Uses the application factory pattern with lifespan management.

Why an app factory?
- Lifespan events handle startup/shutdown (DB pool, Redis, MinIO bucket check)
- Middleware registration is centralized
- CORS is configured from environment variables
- OpenAPI documentation is customized for the enterprise context
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import router as v1_router
from app.api.middleware.error_handler import register_error_handlers
from app.dependencies import _get_engine

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.

    Startup:
    - Verify database connectivity
    - Log configuration summary

    Shutdown:
    - Dispose database engine (close all pool connections)
    """
    settings = get_settings()
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        environment=settings.app_env,
        debug=settings.debug,
    )

    # Verify database connectivity
    engine = _get_engine(settings)
    try:
        async with engine.begin() as conn:
            await conn.execute(
                __import__("sqlalchemy").text("SELECT 1")
            )
        logger.info("database_connected", host=settings.postgres_host)
    except Exception as e:
        logger.error("database_connection_failed", error=str(e))
        raise

    yield  # Application runs here

    # Shutdown
    logger.info("application_shutting_down")
    await engine.dispose()
    logger.info("database_pool_disposed")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description=(
            "Enterprise Investment Intelligence Operating System. "
            "AI-powered due diligence platform for investment analysts."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Error Handlers ──
    register_error_handlers(app)

    # ── Routers ──
    app.include_router(v1_router)

    # ── Root Health Check ──
    @app.get("/health", tags=["System"])
    async def root_health():
        """Root health check for load balancer probes."""
        return {"status": "healthy", "service": "dealos-ai"}

    return app


# Module-level app instance for uvicorn
app = create_app()
