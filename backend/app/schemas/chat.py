"""
DealOS AI — Chat Schemas.

Pydantic models for the LangGraph orchestration chat API.

Request schemas:
  - ChatQueryRequest: Question + company_id + optional session_id
  - ChatStreamRequest: Same as query but for SSE streaming

Response schemas:
  - ChatQueryResponse: Full structured response with recommendation
  - ChatStreamEvent: Individual SSE event during streaming
  - ChatSessionResponse: Session metadata for history listing
  - ChatSessionDetailResponse: Session with full message history
  - ChatMessageResponse: Individual message in a session
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# ── Request Schemas ──


class ChatQueryRequest(BaseModel):
    """Request body for POST /api/v1/chat/query and /chat/stream."""

    question: str = Field(
        min_length=1,
        max_length=2000,
        description="The investment analysis question to answer",
    )
    company_id: UUID = Field(
        description="Company workspace to scope the analysis to",
    )
    session_id: UUID | None = Field(
        default=None,
        description="Optional: continue an existing conversation. "
                    "If omitted, a new session is created.",
    )


# ── Agent Trace Schema ──


class AgentTraceItem(BaseModel):
    """Execution trace for a single agent in the pipeline."""

    name: str = Field(description="Agent name (planner, financial, risk, company, committee)")
    status: str = Field(description="Execution status: completed, skipped, error")
    duration_ms: int = Field(default=0, description="Execution time in milliseconds")
    summary: str | None = Field(default=None, description="Brief output summary")


class AgentTrace(BaseModel):
    """Full execution trace for the multi-agent pipeline."""

    agents: list[AgentTraceItem] = Field(default_factory=list)
    total_duration_ms: int = Field(default=0)
    execution_plan: list[str] = Field(default_factory=list)


# ── Response Schemas ──


class ChatQueryResponse(BaseModel):
    """Response body for POST /api/v1/chat/query."""

    session_id: str
    message_id: str
    answer: str = Field(description="Full synthesized answer from the Investment Committee")
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for the recommendation",
    )
    agent_trace: AgentTrace = Field(
        default_factory=AgentTrace,
        description="Execution trace showing which agents ran and their results",
    )
    company_id: str


class ChatStreamEvent(BaseModel):
    """Individual SSE event during streaming."""

    event: str = Field(
        description="Event type: status, chunk, agent_complete, done, error"
    )
    data: str = Field(description="Event payload text")
    agent: str | None = Field(default=None, description="Agent name if applicable")


# ── Session & History Schemas ──


class ChatMessageResponse(BaseModel):
    """A single message in a chat session."""

    id: UUID
    role: str
    content: str
    citations: list[dict] | None = None
    agent_trace: dict | None = None
    token_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionResponse(BaseModel):
    """Session metadata for history listing."""

    id: UUID
    title: str
    status: str
    company_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetailResponse(BaseModel):
    """Session with full message history."""

    id: UUID
    title: str
    status: str
    company_id: UUID
    user_id: UUID
    messages: list[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Response for GET /api/v1/chat/history."""

    sessions: list[ChatSessionResponse]
    total_sessions: int
    company_id: str
