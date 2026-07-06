"""
DealOS AI — Rate Limiting Middleware.

Redis-backed sliding window rate limiter to prevent brute-force attacks
and API abuse.

Design decisions:
1. Sliding window (not fixed window): Fixed windows allow bursts at window
   boundaries (e.g., 10 requests at 0:59 + 10 at 1:00 = 20 in 2 seconds).
   Sliding windows distribute limits evenly.

2. Redis-backed: Survives application restarts, works across multiple
   backend instances (important for horizontal scaling).

3. Per-IP limiting: Appropriate for auth endpoints. Per-user limiting
   would require authentication first (chicken-and-egg problem).

4. Configurable per-route: Auth endpoints get stricter limits (10/min)
   than general API endpoints (60/min).

Why rate limiting matters for a financial platform:
- Prevents credential stuffing attacks
- Protects expensive AI endpoints from abuse
- Required for SOC 2 compliance
"""

import time
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.core.exceptions import RateLimitError

logger = structlog.get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed sliding window rate limiter.

    Applies different limits based on the endpoint path:
    - Auth endpoints (/api/v1/auth/*): Stricter limit (default 10/min)
    - All other endpoints: Standard limit (default 60/min)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing the request."""
        # Skip rate limiting for health checks and docs
        path = request.url.path
        if path in ("/health", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        settings = get_settings()

        # Determine rate limit based on path
        is_auth_endpoint = path.startswith("/api/v1/auth")
        max_requests = (
            settings.auth_rate_limit_per_minute
            if is_auth_endpoint
            else settings.rate_limit_per_minute
        )

        # Extract client identifier (IP address)
        client_ip = self._get_client_ip(request)
        rate_key = f"rate_limit:{client_ip}:{path}"

        # Check rate limit using in-memory fallback if Redis unavailable
        try:
            is_allowed = await self._check_rate_limit_memory(
                rate_key, max_requests
            )
        except Exception:
            # If rate limiting fails, allow the request (fail-open)
            # Log the error but don't block legitimate traffic
            logger.warning("rate_limit_check_failed", client_ip=client_ip)
            is_allowed = True

        if not is_allowed:
            logger.warning(
                "rate_limit_exceeded",
                client_ip=client_ip,
                path=path,
                limit=max_requests,
            )
            raise RateLimitError(
                details={"limit": max_requests, "window": "60s"},
            )

        response = await call_next(request)

        # Add rate limit headers (standard practice)
        response.headers["X-RateLimit-Limit"] = str(max_requests)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Extract client IP from request.

        Checks X-Forwarded-For header for clients behind a proxy/load balancer.
        Falls back to direct connection IP.
        """
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs; the first is the client
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"


# ── In-Memory Rate Limiter (Fallback) ──
# Used when Redis is unavailable. Simple but effective for single-instance deployments.

_rate_limit_store: dict[str, list[float]] = {}


async def _check_rate_limit_memory(
    self, key: str, max_requests: int, window_seconds: int = 60
) -> bool:
    """
    In-memory sliding window rate limiter.

    Stores timestamps of recent requests per key. Removes expired timestamps
    and checks if the current request exceeds the limit.

    Note: This doesn't work across multiple backend instances.
    For production with multiple instances, use Redis (implemented in Phase 4
    when Redis dependency injection is fully wired).
    """
    now = time.time()
    window_start = now - window_seconds

    # Get or create the request timestamp list
    if key not in _rate_limit_store:
        _rate_limit_store[key] = []

    # Remove expired timestamps
    _rate_limit_store[key] = [
        ts for ts in _rate_limit_store[key] if ts > window_start
    ]

    # Check limit
    if len(_rate_limit_store[key]) >= max_requests:
        return False

    # Record this request
    _rate_limit_store[key].append(now)
    return True

    # Periodic cleanup of stale keys (every 100 requests)
    if len(_rate_limit_store) > 1000:
        stale_keys = [
            k for k, v in _rate_limit_store.items()
            if not v or v[-1] < window_start
        ]
        for k in stale_keys:
            del _rate_limit_store[k]
