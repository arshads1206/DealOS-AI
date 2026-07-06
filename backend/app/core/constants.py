"""
DealOS AI — Application Constants.

Centralized enums and constants prevent magic strings scattered across the codebase.
Using Python enums (with str mixin) ensures type safety and serialization compatibility.
"""

from enum import StrEnum


class UserRole(StrEnum):
    """
    User roles for RBAC.

    Why these four roles?
    - ADMIN: Platform administration, user management, system configuration.
    - ANALYST: Primary users — upload documents, run analysis, generate memos.
    - REVIEWER: Senior staff who review analyst work, can generate reports but not upload.
    - VIEWER: Read-only access for stakeholders who need visibility without edit rights.

    This mirrors the hierarchy at investment banks:
    MD/VP (admin) → Associate/Analyst (analyst) → IC Member (reviewer) → Client (viewer)
    """

    ADMIN = "admin"
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class DocumentStatus(StrEnum):
    """Document processing lifecycle states."""

    UPLOADED = "uploaded"      # File stored, processing not yet started
    PROCESSING = "processing"  # Parsing, chunking, embedding in progress
    PROCESSED = "processed"    # Successfully processed and searchable
    FAILED = "failed"          # Processing failed (see error_message)


class TaskStatus(StrEnum):
    """Background task lifecycle states."""

    PENDING = "pending"        # Queued, waiting for worker
    RUNNING = "running"        # Currently executing
    COMPLETED = "completed"    # Successfully finished
    FAILED = "failed"          # Failed (see error_message)
    CANCELLED = "cancelled"    # Cancelled by user or system


class ReportType(StrEnum):
    """Types of generated reports."""

    INVESTMENT_MEMO = "investment_memo"
    RISK_REPORT = "risk_report"
    FINANCIAL_SUMMARY = "financial_summary"


class ReportStatus(StrEnum):
    """Report generation lifecycle states."""

    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class RiskSeverity(StrEnum):
    """
    Risk severity levels.

    Aligned with enterprise risk frameworks (ISO 31000):
    - CRITICAL: Immediate threat to investment thesis
    - HIGH: Significant concern requiring mitigation
    - MEDIUM: Notable risk worth monitoring
    - LOW: Minor concern with limited impact
    - INFO: Informational finding, not a risk
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class PeriodType(StrEnum):
    """Financial reporting period types."""

    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    TTM = "ttm"  # Trailing Twelve Months


class NotificationType(StrEnum):
    """Notification severity/type indicators."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class MessageRole(StrEnum):
    """Chat message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatSessionStatus(StrEnum):
    """Chat session lifecycle states."""

    ACTIVE = "active"
    ARCHIVED = "archived"


# ── Limits & Defaults ──

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
MAX_CHUNKS_PER_DOCUMENT = 1000
MAX_SEARCH_RESULTS = 50
EMBEDDING_BATCH_SIZE = 100
BM25_TOP_K = 50
VECTOR_TOP_K = 50
RERANKER_TOP_K = 10
