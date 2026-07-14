"""
DealOS AI — Chat Repository.

Data access layer for chat sessions and messages.
Extends CRUDRepository with conversation-specific queries:
session history, message creation, and company-scoped listing.

Chat sessions are scoped to a company workspace — each company has
its own conversation history that agents can reference.
"""

import uuid
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.constants import ChatSessionStatus, MessageRole
from app.models.chat import ChatSession, Message
from app.repositories.base import CRUDRepository


class ChatRepository(CRUDRepository[ChatSession]):
    """Chat session and message data access."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(ChatSession, session)

    async def create_session(
        self,
        company_id: UUID,
        user_id: UUID,
        title: str = "New Conversation",
    ) -> ChatSession:
        """Create a new chat session scoped to a company workspace."""
        chat_session = ChatSession(
            company_id=company_id,
            user_id=user_id,
            title=title,
            status=ChatSessionStatus.ACTIVE,
        )
        self._session.add(chat_session)
        await self._session.flush()
        await self._session.refresh(chat_session)
        return chat_session

    async def get_session_with_messages(
        self,
        session_id: UUID,
    ) -> ChatSession | None:
        """
        Get a chat session with all its messages eagerly loaded.

        Messages are ordered by created_at ascending (chronological).
        """
        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_company(
        self,
        company_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ChatSession]:
        """
        List chat sessions for a company, scoped to the requesting user.

        Returns sessions ordered by most recently updated first.
        """
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.company_id == company_id,
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == False,  # noqa: E712
            )
            .order_by(ChatSession.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def create_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        citations: list[dict] | None = None,
        agent_trace: dict | None = None,
        token_count: int = 0,
    ) -> Message:
        """
        Create a new message in a chat session.

        Args:
            session_id: Parent chat session.
            role: Message role (user, assistant, system).
            content: Message text content.
            citations: Optional list of source citations.
            agent_trace: Optional agent execution trace for observability.
            token_count: Token count for usage tracking.
        """
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            citations=citations or [],
            agent_trace=agent_trace or {},
            token_count=token_count,
        )
        self._session.add(message)
        await self._session.flush()
        await self._session.refresh(message)
        return message

    async def get_recent_messages(
        self,
        session_id: UUID,
        limit: int = 20,
    ) -> list[Message]:
        """
        Get the most recent messages from a session for conversation memory.

        Returns messages in chronological order (oldest first).
        """
        # Subquery to get the last N message IDs
        subquery = (
            select(Message.id)
            .where(
                Message.session_id == session_id,
                Message.is_deleted == False,  # noqa: E712
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        stmt = (
            select(Message)
            .where(Message.id.in_(subquery))
            .order_by(Message.created_at.asc())
        )

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def count_sessions_by_company(
        self,
        company_id: UUID,
        user_id: UUID,
    ) -> int:
        """Count total chat sessions for a company workspace."""
        stmt = (
            select(func.count())
            .select_from(ChatSession)
            .where(
                ChatSession.company_id == company_id,
                ChatSession.user_id == user_id,
                ChatSession.is_deleted == False,  # noqa: E712
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()
