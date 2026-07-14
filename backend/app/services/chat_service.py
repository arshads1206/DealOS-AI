"""
DealOS AI — Chat Service.

Orchestrates the LangGraph multi-agent pipeline with conversation memory
and session persistence. This is the bridge between the API layer and
the LangGraph graph execution.

Responsibilities:
1. Session management: Create/resume chat sessions
2. Memory management: Load recent messages as conversation context
3. Graph execution: Invoke run_graph or stream_graph
4. Persistence: Store user questions and assistant responses in DB
5. Agent trace recording: Store execution metadata for observability

The service never performs retrieval, extraction, or analysis directly.
All intelligence work is delegated through the graph to existing services.
"""

import json
import time
from typing import AsyncGenerator
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agents.graph import run_graph, stream_graph
from app.core.constants import MessageRole
from app.core.exceptions import NotFoundError
from app.repositories.chat_repository import ChatRepository
from app.repositories.company_repository import CompanyRepository
from app.schemas.chat import (
    AgentTrace,
    AgentTraceItem,
    ChatHistoryResponse,
    ChatMessageResponse,
    ChatQueryResponse,
    ChatSessionDetailResponse,
    ChatSessionResponse,
    ChatStreamEvent,
)

logger = structlog.get_logger(__name__)

# Maximum messages to load for conversation context
MAX_MEMORY_MESSAGES = 20


class ChatService:
    """
    Multi-agent chat orchestrator.

    Manages the lifecycle: Session → Memory → Graph → Persistence → Response
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._chat_repo = ChatRepository(session)
        self._company_repo = CompanyRepository(session)

    # ═══════════════════════════════════════════════════════════════
    # Query (blocking)
    # ═══════════════════════════════════════════════════════════════

    async def query(
        self,
        question: str,
        company_id: UUID,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> ChatQueryResponse:
        """
        Execute a full investment analysis query.

        Creates or resumes a session, loads memory, runs the graph,
        persists results, and returns a structured response.

        Args:
            question: User's investment question.
            company_id: Company workspace scope.
            user_id: Requesting user's ID.
            session_id: Optional existing session to continue.

        Returns:
            ChatQueryResponse with full recommendation and agent traces.
        """
        start = time.time()

        logger.info(
            "chat_query_start",
            question_preview=question[:100],
            company_id=str(company_id),
            session_id=str(session_id) if session_id else "new",
        )

        # Validate company exists
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        # Get or create session
        chat_session = await self._get_or_create_session(
            session_id=session_id,
            company_id=company_id,
            user_id=user_id,
            question=question,
        )

        # Load conversation memory
        memory = await self._load_memory(chat_session.id)

        # Store user message
        await self._chat_repo.create_message(
            session_id=chat_session.id,
            role=MessageRole.USER,
            content=question,
        )

        # Execute graph
        final_state = await run_graph(
            question=question,
            company_id=str(company_id),
            session_id=str(chat_session.id),
            session=self._session,
            messages=memory,
        )

        # Extract results
        answer = final_state.get("committee_result", "No recommendation generated.")
        confidence = final_state.get("confidence", 0.0)
        agent_traces = final_state.get("agent_traces", [])

        # Build agent trace
        trace = AgentTrace(
            agents=[AgentTraceItem(**t) for t in agent_traces],
            total_duration_ms=int((time.time() - start) * 1000),
            execution_plan=final_state.get("execution_plan", []),
        )

        # Store assistant response
        assistant_msg = await self._chat_repo.create_message(
            session_id=chat_session.id,
            role=MessageRole.ASSISTANT,
            content=answer,
            agent_trace=trace.model_dump(),
        )

        # Update session title from first question
        if len(memory) == 0:
            title = question[:100] + ("..." if len(question) > 100 else "")
            await self._chat_repo.update(chat_session.id, title=title)

        logger.info(
            "chat_query_complete",
            session_id=str(chat_session.id),
            confidence=confidence,
            duration_ms=trace.total_duration_ms,
        )

        return ChatQueryResponse(
            session_id=str(chat_session.id),
            message_id=str(assistant_msg.id),
            answer=answer,
            confidence=confidence,
            agent_trace=trace,
            company_id=str(company_id),
        )

    # ═══════════════════════════════════════════════════════════════
    # Stream (SSE)
    # ═══════════════════════════════════════════════════════════════

    async def stream(
        self,
        question: str,
        company_id: UUID,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> AsyncGenerator[ChatStreamEvent, None]:
        """
        Stream the graph execution as SSE events.

        Yields status updates as each agent node completes, providing
        real-time progress feedback to the frontend.

        Event types:
            status       → Agent starting/completing
            agent_complete → Agent finished with summary
            chunk        → Final answer text
            done         → Execution complete
            error        → Error occurred
        """
        start = time.time()

        logger.info(
            "chat_stream_start",
            question_preview=question[:100],
            company_id=str(company_id),
        )

        # Validate company
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            yield ChatStreamEvent(
                event="error",
                data=f"Company not found: {company_id}",
            )
            return

        # Get or create session
        chat_session = await self._get_or_create_session(
            session_id=session_id,
            company_id=company_id,
            user_id=user_id,
            question=question,
        )

        # Load memory
        memory = await self._load_memory(chat_session.id)

        # Store user message
        await self._chat_repo.create_message(
            session_id=chat_session.id,
            role=MessageRole.USER,
            content=question,
        )

        yield ChatStreamEvent(
            event="status",
            data="Planning analysis...",
            agent="planner",
        )

        # Stream graph execution
        final_answer = ""
        confidence = 0.0
        agent_traces: list[dict] = []

        try:
            async for node_name, state_update in stream_graph(
                question=question,
                company_id=str(company_id),
                session_id=str(chat_session.id),
                session=self._session,
                messages=memory,
            ):
                # Emit status updates based on node name
                if node_name == "planner":
                    plan = state_update.get("execution_plan", [])
                    yield ChatStreamEvent(
                        event="agent_complete",
                        data=f"Analysis plan: {', '.join(plan)}",
                        agent="planner",
                    )
                    # Announce upcoming agents
                    for agent_name in plan:
                        yield ChatStreamEvent(
                            event="status",
                            data=f"Running {agent_name} analysis...",
                            agent=agent_name,
                        )

                elif node_name == "financial":
                    yield ChatStreamEvent(
                        event="agent_complete",
                        data="Financial analysis complete.",
                        agent="financial",
                    )

                elif node_name == "risk":
                    yield ChatStreamEvent(
                        event="agent_complete",
                        data="Risk analysis complete.",
                        agent="risk",
                    )

                elif node_name == "company":
                    yield ChatStreamEvent(
                        event="agent_complete",
                        data="Company analysis complete.",
                        agent="company",
                    )

                elif node_name == "committee":
                    yield ChatStreamEvent(
                        event="status",
                        data="Generating investment recommendation...",
                        agent="committee",
                    )
                    final_answer = state_update.get("committee_result", "")
                    confidence = state_update.get("confidence", 0.0)

                # Collect traces
                node_traces = state_update.get("agent_traces", [])
                agent_traces.extend(node_traces)

            # Emit the final answer
            if final_answer:
                yield ChatStreamEvent(
                    event="chunk",
                    data=final_answer,
                    agent="committee",
                )

            # Build trace and persist
            trace = AgentTrace(
                agents=[AgentTraceItem(**t) for t in agent_traces],
                total_duration_ms=int((time.time() - start) * 1000),
                execution_plan=[],
            )

            await self._chat_repo.create_message(
                session_id=chat_session.id,
                role=MessageRole.ASSISTANT,
                content=final_answer or "No recommendation generated.",
                agent_trace=trace.model_dump(),
            )

            # Update session title
            if len(memory) == 0:
                title = question[:100] + ("..." if len(question) > 100 else "")
                await self._chat_repo.update(chat_session.id, title=title)

            yield ChatStreamEvent(
                event="done",
                data=json.dumps({
                    "session_id": str(chat_session.id),
                    "confidence": confidence,
                    "total_duration_ms": trace.total_duration_ms,
                }),
            )

        except Exception as e:
            logger.error("chat_stream_error", error=str(e))
            yield ChatStreamEvent(
                event="error",
                data=f"Stream error: {str(e)}",
            )

    # ═══════════════════════════════════════════════════════════════
    # Session History
    # ═══════════════════════════════════════════════════════════════

    async def get_history(
        self,
        company_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> ChatHistoryResponse:
        """Get chat session history for a company workspace."""
        company = await self._company_repo.get_by_id(company_id)
        if company is None:
            raise NotFoundError(resource="Company", resource_id=str(company_id))

        sessions = await self._chat_repo.list_by_company(
            company_id=company_id,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
        total = await self._chat_repo.count_sessions_by_company(
            company_id=company_id,
            user_id=user_id,
        )

        return ChatHistoryResponse(
            sessions=[ChatSessionResponse.model_validate(s) for s in sessions],
            total_sessions=total,
            company_id=str(company_id),
        )

    async def get_session(
        self,
        session_id: UUID,
    ) -> ChatSessionDetailResponse:
        """Get a chat session with full message history."""
        chat_session = await self._chat_repo.get_session_with_messages(session_id)
        if chat_session is None:
            raise NotFoundError(resource="ChatSession", resource_id=str(session_id))

        return ChatSessionDetailResponse(
            id=chat_session.id,
            title=chat_session.title,
            status=chat_session.status,
            company_id=chat_session.company_id,
            user_id=chat_session.user_id,
            messages=[
                ChatMessageResponse.model_validate(m) for m in chat_session.messages
            ],
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at,
        )

    # ═══════════════════════════════════════════════════════════════
    # Internal Helpers
    # ═══════════════════════════════════════════════════════════════

    async def _get_or_create_session(
        self,
        session_id: UUID | None,
        company_id: UUID,
        user_id: UUID,
        question: str,
    ):
        """Get an existing session or create a new one."""
        if session_id:
            existing = await self._chat_repo.get_by_id(session_id)
            if existing:
                return existing

        # Create new session
        return await self._chat_repo.create_session(
            company_id=company_id,
            user_id=user_id,
            title="New Conversation",
        )

    async def _load_memory(self, session_id: UUID) -> list[dict]:
        """
        Load recent messages as conversation memory.

        Returns a list of {role, content} dicts for the graph's messages field.
        """
        messages = await self._chat_repo.get_recent_messages(
            session_id=session_id,
            limit=MAX_MEMORY_MESSAGES,
        )

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
