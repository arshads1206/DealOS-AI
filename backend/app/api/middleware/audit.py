"""
DealOS AI — Audit Logging Middleware.

Automatically creates audit log entries for significant API actions.
Runs AFTER the request is processed, so it captures the response status.

What gets audited:
- All POST, PUT, PATCH, DELETE requests (state-changing operations)
- Excludes GET requests (reads don't need audit trails in most cases)
- Excludes health checks and documentation endpoints

This middleware provides a "free" audit trail — endpoints don't need
to manually create audit entries for basic CRUD operations. The more
detailed audit logging (with old/new values) is done in the service layer.

Why middleware instead of service-only logging?
- Catches operations that skip the service layer (rare but possible)
- Provides IP address and user-agent context
- Ensures no state change goes unrecorded
- Defense in depth
"""

import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger(__name__)

# Paths that should NOT be audited
_EXCLUDED_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/health",
}

# Only audit state-changing methods
_AUDITED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs state-changing API requests to structured logs.

    Note: This creates STRUCTURED LOG entries (via structlog), not database
    audit log records. Database audit records are created in the service layer
    where we have access to the database session and old/new values.

    The structured logs are shipped to a log aggregator (ELK, Datadog, Splunk)
    for compliance reporting and security monitoring.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log significant API actions after processing."""
        path = request.url.path

        # Skip excluded paths
        if path in _EXCLUDED_PATHS or request.method not in _AUDITED_METHODS:
            return await call_next(request)

        # Extract client info
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "unknown")

        # Extract user info from JWT (if present in auth header)
        user_id = self._extract_user_id(request)

        # Process the request
        response = await call_next(request)

        # Log the action
        logger.info(
            "api_audit",
            method=request.method,
            path=path,
            status_code=response.status_code,
            user_id=user_id,
            client_ip=client_ip,
            user_agent=user_agent[:200],  # Truncate to prevent log bloat
        )

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, considering proxy headers."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _extract_user_id(self, request: Request) -> str | None:
        """
        Extract user ID from the Authorization header without full validation.

        This is a best-effort extraction for logging purposes only.
        The actual auth validation is done by the auth middleware/dependency.
        We decode the JWT payload without verification to avoid duplicating
        the crypto work.
        """
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return None

        try:
            import jwt as pyjwt

            token = auth_header.split(" ", 1)[1]
            # Decode WITHOUT verification — just for logging
            payload = pyjwt.decode(
                token, options={"verify_signature": False}
            )
            return payload.get("sub")
        except Exception:
            return None
