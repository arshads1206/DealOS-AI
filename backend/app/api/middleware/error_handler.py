"""
DealOS AI — Global Error Handler Middleware.

Maps application exceptions to consistent JSON error responses.
Catches both custom DealOSError exceptions and unexpected errors.

Response format:
{
    "error": {
        "code": "NOT_FOUND",
        "message": "Company with id 'abc' not found",
        "details": {}
    }
}

Why a global handler instead of per-endpoint try/catch?
- DRY: Error formatting logic in one place
- Consistency: Every error response has the same shape
- Safety: Unexpected exceptions return 500 without leaking internals
- Logging: All errors are centrally logged
"""

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import DealOSError

logger = structlog.get_logger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI application."""

    @app.exception_handler(DealOSError)
    async def dealos_error_handler(request: Request, exc: DealOSError) -> JSONResponse:
        """Handle all custom application errors."""
        logger.warning(
            "application_error",
            error_code=exc.error_code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
            method=request.method,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """
        Catch-all for unexpected errors.

        NEVER expose internal error details in production.
        The actual exception is logged for debugging.
        """
        logger.error(
            "unhandled_error",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=str(request.url),
            method=request.method,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )
