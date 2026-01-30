# Spec: conversational-state

**File**: `specs/conversational-state/spec.md`

**Generated**: 2026-01-31
**Change**: c010-voice-client

---

## 1.1 Purpose

Define conversational state management for tracking voice conversation history, context, and session persistence. This spec covers message tracking, context window management, and integration with C003 agent pipeline.

---

## 1.2 Scope

**In Scope**:
- ConversationSession entity for tracking sessions
- Message entity for user/assistant messages
- Context entity for conversation context (topic, entities, sentiment)
- ConversationStateManager for CRUD operations
- Session persistence and recovery
- Context injection into C003 agent queries

**Out of Scope**:
- WebSocket connection management (covered by voice-gateway spec)
- Audio processing (handled by kyutai)
- Long-term memory (covered by C005 memory-rag)

---

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CS-001 | System MUST track user and assistant messages with timestamps | Must |
| FR-CS-002 | System MUST maintain conversation context (topic, entities, sentiment) | Must |
| FR-CS-003 | System MUST support session persistence across WebSocket reconnections | Must |
| FR-CS-004 | System MUST inject conversation history into C003 agent queries | Must |
| FR-CS-005 | System MUST support context window limiting (max 20 messages) | Must |
| FR-CS-006 | System MUST clean up inactive sessions after 5 minutes | Must |
| FR-CS-007 | System MUST provide REST endpoint for retrieving conversation history | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-CS-001 | ConversationStateManager MUST use absolute imports only | Must |
| NFR-CS-002 | ConversationStateManager MUST pass ruff check and ruff format | Must |
| NFR-CS-003 | ConversationStateManager MUST pass pyrefly type checking | Must |
| NFR-CS-004 | ConversationStateManager file MUST NOT exceed 150 lines | Must |
| NFR-CS-005 | Session state MUST be stored in-memory (no database for MVP) | Must |

---

## 1.4 Data Model

### File: agentx/domain/entities/conversation_session.py

```python
"""Conversation session domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class MessageRole(str, Enum):
    """Message role in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ConversationMessage:
    """A single message in a conversation.

    Attributes:
        message_id: Unique message identifier.
        role: Message role (user, assistant, system).
        content: Message content (text).
        timestamp: Message timestamp.
        metadata: Optional metadata (entities, sentiment, etc.).
    """

    message_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None


@dataclass
class ConversationContext:
    """Conversation context for multi-turn interactions.

    Attributes:
        current_topic: Current conversation topic.
        entities: Extracted entities (names, places, etc.).
        sentiment: Conversation sentiment (positive, neutral, negative).
        language: Conversation language.
        timezone: User timezone.
    """

    current_topic: str | None = None
    entities: dict[str, Any] | None = None
    sentiment: str | None = None
    language: str = "en"
    timezone: str = "UTC"


@dataclass
class ConversationSession:
    """A voice conversation session.

    Attributes:
        session_id: Unique session identifier.
        messages: List of messages in the session.
        context: Conversation context.
        created_at: Session creation timestamp.
        last_activity_at: Last activity timestamp.
    """

    session_id: UUID
    messages: list[ConversationMessage] = field(default_factory=list)
    context: ConversationContext = field(default_factory=ConversationContext)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, message: ConversationMessage) -> None:
        """Add a message to the session.

        Args:
            message: Message to add.
        """
        self.messages.append(message)
        self.last_activity_at = datetime.utcnow()

    def get_history(self, limit: int = 20) -> list[ConversationMessage]:
        """Get conversation history with limit.

        Args:
            limit: Maximum number of messages to return.

        Returns:
            List of messages, most recent first.
        """
        return self.messages[-limit:]

    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if session is expired.

        Args:
            timeout_seconds: Timeout in seconds (default: 300 = 5 minutes).

        Returns:
            True if session is expired, False otherwise.
        """
        delta = datetime.utcnow() - self.last_activity_at
        return delta.total_seconds() > timeout_seconds
```

### File: agentx/application/use_cases/conversation_state_manager.py

```python
"""Conversation state manager use case."""

import asyncio
from datetime import datetime
from typing import Awaitable, Callable
from uuid import UUID, uuid4

from agentx.domain.entities.conversation_session import (
    ConversationMessage,
    ConversationSession,
    MessageRole,
)


class ConversationStateManager:
    """Manage conversation state for voice sessions.

    Provides in-memory storage and cleanup for conversation sessions.
    """

    def __init__(self) -> None:
        """Initialize conversation state manager."""
        self._sessions: dict[UUID, ConversationSession] = {}
        self._cleanup_task: asyncio.Task[None] | None = None
        self._cleanup_interval = 60  # Check every 60 seconds
        self._session_timeout = 300  # 5 minutes

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

    def get_or_create_session(self, session_id: UUID | None = None) -> ConversationSession:
        """Get or create a conversation session.

        Args:
            session_id: Optional session ID. If None, creates new session.

        Returns:
            Conversation session.
        """
        if session_id is None:
            session_id = uuid4()

        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id=session_id)

        return self._sessions[session_id]

    def add_user_message(self, session_id: UUID, content: str) -> ConversationMessage:
        """Add a user message to the session.

        Args:
            session_id: Session identifier.
            content: Message content.

        Returns:
            Created message.
        """
        session = self.get_or_create_session(session_id)
        message = ConversationMessage(
            message_id=uuid4(),
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.utcnow(),
        )
        session.add_message(message)
        return message

    def add_assistant_message(self, session_id: UUID, content: str) -> ConversationMessage:
        """Add an assistant message to the session.

        Args:
            session_id: Session identifier.
            content: Message content.

        Returns:
            Created message.
        """
        session = self.get_or_create_session(session_id)
        message = ConversationMessage(
            message_id=uuid4(),
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.utcnow(),
        )
        session.add_message(message)
        return message

    def get_conversation_history(self, session_id: UUID, limit: int = 20) -> list[ConversationMessage]:
        """Get conversation history for a session.

        Args:
            session_id: Session identifier.
            limit: Maximum number of messages to return.

        Returns:
            List of messages.
        """
        session = self._sessions.get(session_id)
        if session:
            return session.get_history(limit)
        return []

    def update_context(self, session_id: UUID, **kwargs) -> None:
        """Update conversation context.

        Args:
            session_id: Session identifier.
            **kwargs: Context fields to update.
        """
        session = self._sessions.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session.context, key):
                    setattr(session.context, key, value)

    def get_session(self, session_id: UUID) -> ConversationSession | None:
        """Get a conversation session.

        Args:
            session_id: Session identifier.

        Returns:
            Conversation session or None.
        """
        return self._sessions.get(session_id)

    def delete_session(self, session_id: UUID) -> None:
        """Delete a conversation session.

        Args:
            session_id: Session identifier.
        """
        self._sessions.pop(session_id, None)
```

---

## 1.5 API Contract

### REST Endpoints

| Method | Path | Request | Response | Status Codes |
|--------|------|---------|----------|--------------|
| GET | `/api/v1/voice/conversation/history?session_id={id}&limit={limit}` | - | `list[ConversationMessageDTO]` | 200, 404, 500 |
| POST | `/api/v1/voice/conversation/context` | `UpdateContextRequest` | `ConversationContextDTO` | 200, 400, 500 |

---

## 1.6 Acceptance Criteria

- [ ] ConversationSession entity tracks messages with timestamps
- [ ] ConversationContext tracks topic, entities, sentiment
- [ ] ConversationStateManager provides CRUD operations
- [ ] Session persistence works across WebSocket reconnections
- [ ] Context injection into C003 agent queries works
- [ ] Context window limiting (max 20 messages) works
- [ ] Session cleanup after 5 minutes works
- [ ] REST endpoint for conversation history works
- [ ] ConversationStateManager passes ruff check, ruff format, pyrefly check
- [ ] ConversationStateManager file under 150 lines

---

**Related Specs**:
- `voice-gateway` - Backend service for routing messages
- `voice-client` - Frontend WebSocket client
- C003 agent pipeline - LLM integration

---
