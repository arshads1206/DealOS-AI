"""
DealOS AI — Chat API Endpoints.

REST API for the LangGraph multi-agent investment analyst:

    POST /api/v1/chat/query     — Execute full analysis (blocking)
    POST /api/v1/chat/stream    — Execute with SSE streaming
    GET  /api/v1/chat/history   — List chat sessions for a company
    GET  /api/v1/chat/session/{id} — Get session with full messages

All endpoints use CHAT_WITH_AI permission (admin, analyst, reviewer).
Follows existing patterns: DI via FastAPI Depends, CurrentUser, DbSession.
"""

import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.middleware.auth import CurrentUser
from app.core.permissions import Permission, PermissionChecker
from app.dependencies import DbSession
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatQueryRequest,
    ChatQueryResponse,
    ChatSessionDetailResponse,
)
from app.services.chat_service import ChatService

router = APIRouter()


@router.post(
    "/query",
    response_model=ChatQueryResponse,
    summary="Ask the AI Investment Analyst",
    responses={
        200: {"description": "Investment analysis recommendation"},
        404: {"description": "Company not found"},
        422: {"description": "Invalid request"},
    },
)
async def chat_query(
    request: ChatQueryRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.CHAT_WITH_AI)),
):
    """
    Execute a full multi-agent investment analysis.

    The AI Investment Analyst processes your question through:
    1. **Planner Agent** — determines which specialists to invoke
    2. **Financial Analyst** — analyzes financial metrics and performance
    3. **Risk Analyst** — assesses risk findings and severity
    4. **Company Analyst** — reviews business profile and competitive position
    5. **Investment Committee** — synthesizes a final recommendation

    Supports follow-up questions within a session for multi-turn conversations.
    Pass `session_id` to continue an existing conversation.
    """
    service = ChatService(db)
    return await service.query(
        question=request.question,
        company_id=request.company_id,
        user_id=uuid.UUID(current_user["user_id"]),
        session_id=request.session_id,
    )


@router.post(
    "/stream",
    summary="Stream AI Investment Analysis",
    responses={
        200: {
            "description": "SSE stream of analysis events",
            "content": {"text/event-stream": {}},
        },
        404: {"description": "Company not found"},
    },
)
async def chat_stream(
    request: ChatQueryRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.CHAT_WITH_AI)),
):
    """
    Stream the multi-agent analysis with real-time status updates.

    Returns a Server-Sent Events (SSE) stream with events:
    - `status` — Agent starting/progressing
    - `agent_complete` — Agent finished with summary
    - `chunk` — Final answer text
    - `done` — Execution complete with metadata
    - `error` — Error occurred

    Frontend can display progress like:
    "Planning analysis..." → "Running financial analysis..." → "Complete"
    """
    service = ChatService(db)

    async def event_generator():
        async for event in service.stream(
            question=request.question,
            company_id=request.company_id,
            user_id=uuid.UUID(current_user["user_id"]),
            session_id=request.session_id,
        ):
            yield f"event: {event.event}\ndata: {event.data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get chat session history",
    responses={
        200: {"description": "List of chat sessions for the company"},
        404: {"description": "Company not found"},
    },
)
async def chat_history(
    company_id: uuid.UUID = Query(description="Company workspace ID"),
    db: DbSession = None,
    current_user: CurrentUser = None,
    _: None = Depends(PermissionChecker(Permission.CHAT_WITH_AI)),
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=20, ge=1, le=100, description="Page size"),
):
    """
    List chat sessions for a company workspace.

    Returns sessions ordered by most recent activity.
    Scoped to the requesting user's sessions only.
    """
    service = ChatService(db)
    return await service.get_history(
        company_id=company_id,
        user_id=uuid.UUID(current_user["user_id"]),
        skip=skip,
        limit=limit,
    )


@router.get(
    "/session/{session_id}",
    response_model=ChatSessionDetailResponse,
    summary="Get chat session with messages",
    responses={
        200: {"description": "Chat session with full message history"},
        404: {"description": "Session not found"},
    },
)
async def chat_session(
    session_id: uuid.UUID,
    db: DbSession,
    current_user: CurrentUser,
    _: None = Depends(PermissionChecker(Permission.CHAT_WITH_AI)),
):
    """
    Get a specific chat session with its full message history.

    Includes all user and assistant messages with agent traces
    and citations for transparency.
    """
    service = ChatService(db)
    return await service.get_session(session_id=session_id)
