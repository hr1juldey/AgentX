"""Conversation state manager use case."""

import asyncio
from datetime import datetime, timezone
from uuid import UUID, uuid4

from agentx.domain.entities.conversation_session import (
    ConversationMessage,
    ConversationSession,
    MessageRole,
)


class ConversationStateManager:
    """Manage conversation state for voice sessions."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, ConversationSession] = {}
        self._cleanup_task: asyncio.Task[None] | None = None
        self._cleanup_interval = 60
        self._session_timeout = 300

    async def start(self) -> None:
        """Start the cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self) -> None:
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None

    async def _cleanup_loop(self) -> None:
        """Cleanup expired sessions."""
        while True:
            await asyncio.sleep(self._cleanup_interval)
            await self._cleanup_expired_sessions()

    async def _cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        expired = [
            session_id
            for session_id, session in self._sessions.items()
            if session.is_expired(self._session_timeout)
        ]
        for session_id in expired:
            del self._sessions[session_id]

    def get_or_create_session(
        self, session_id: UUID | None = None
    ) -> ConversationSession:
        """Get or create a conversation session."""
        if session_id is None:
            session_id = uuid4()

        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id=session_id)

        return self._sessions[session_id]

    def add_user_message(self, session_id: UUID, content: str) -> ConversationMessage:
        """Add a user message to the session."""
        session = self.get_or_create_session(session_id)
        message = ConversationMessage(
            message_id=uuid4(),
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now(timezone.utc),
        )
        session.add_message(message)
        return message

    def add_assistant_message(
        self, session_id: UUID, content: str
    ) -> ConversationMessage:
        """Add an assistant message to the session."""
        session = self.get_or_create_session(session_id)
        message = ConversationMessage(
            message_id=uuid4(),
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.now(timezone.utc),
        )
        session.add_message(message)
        return message

    def get_conversation_history(
        self, session_id: UUID, limit: int = 20
    ) -> list[ConversationMessage]:
        """Get conversation history for a session."""
        session = self._sessions.get(session_id)
        if session:
            return session.get_history(limit)
        return []

    def update_context(self, session_id: UUID, **kwargs) -> None:
        """Update conversation context."""
        session = self._sessions.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session.context, key):
                    setattr(session.context, key, value)

    def get_session(self, session_id: UUID) -> ConversationSession | None:
        """Get a conversation session."""
        return self._sessions.get(session_id)

    def delete_session(self, session_id: UUID) -> None:
        """Delete a conversation session."""
        self._sessions.pop(session_id, None)
