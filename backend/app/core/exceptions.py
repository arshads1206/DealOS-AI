"""
DealOS AI — Custom Exception Hierarchy.

A structured exception tree enables:
1. Consistent API error responses via the global error handler
2. Meaningful error codes that frontends can map to user messages
3. Clean separation between client errors (4xx) and server errors (5xx)

Hierarchy:
    DealOSError (base)
    ├── AuthenticationError (401)
    ├── AuthorizationError (403)
    ├── NotFoundError (404)
    ├── ConflictError (409)
    ├── ValidationError (422)
    ├── RateLimitError (429)
    ├── FileProcessingError (500)
    ├── AIServiceError (500)
    └── ExternalServiceError (502)
"""


class DealOSError(Exception):
    """Base exception for all DealOS application errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: dict | None = None,
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ── Authentication & Authorization ──


class AuthenticationError(DealOSError):
    """Raised when authentication fails (invalid credentials, expired token)."""

    def __init__(
        self,
        message: str = "Authentication failed",
        error_code: str = "AUTH_FAILED",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=401, details=details
        )


class AuthorizationError(DealOSError):
    """Raised when an authenticated user lacks permission for an action."""

    def __init__(
        self,
        message: str = "Insufficient permissions",
        error_code: str = "FORBIDDEN",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=403, details=details
        )


# ── Resource Errors ──


class NotFoundError(DealOSError):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        resource: str = "Resource",
        resource_id: str = "",
        details: dict | None = None,
    ) -> None:
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(
            message=message, error_code="NOT_FOUND", status_code=404, details=details
        )


class ConflictError(DealOSError):
    """Raised when a resource already exists or a conflict occurs."""

    def __init__(
        self,
        message: str = "Resource conflict",
        error_code: str = "CONFLICT",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=409, details=details
        )


class ValidationError(DealOSError):
    """Raised for business logic validation failures beyond Pydantic schema validation."""

    def __init__(
        self,
        message: str = "Validation failed",
        error_code: str = "VALIDATION_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=422, details=details
        )


class RateLimitError(DealOSError):
    """Raised when a client exceeds the rate limit."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code="RATE_LIMITED", status_code=429, details=details
        )


# ── Processing Errors ──


class FileProcessingError(DealOSError):
    """Raised when document parsing, chunking, or embedding fails."""

    def __init__(
        self,
        message: str = "File processing failed",
        error_code: str = "FILE_PROCESSING_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=500, details=details
        )


class AIServiceError(DealOSError):
    """Raised when an AI/LLM operation fails (API timeout, invalid response, etc.)."""

    def __init__(
        self,
        message: str = "AI service error",
        error_code: str = "AI_SERVICE_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=500, details=details
        )


class ExternalServiceError(DealOSError):
    """Raised when an external dependency fails (OpenAI API, MinIO, etc.)."""

    def __init__(
        self,
        message: str = "External service unavailable",
        error_code: str = "EXTERNAL_SERVICE_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message, error_code=error_code, status_code=502, details=details
        )
