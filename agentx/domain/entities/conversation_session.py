"""Conversation session domain entities."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID

from agentx.core.config import get_settings

settings = get_settings()


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


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


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
    created_at: datetime = field(default_factory=_utc_now)
    last_activity_at: datetime = field(default_factory=_utc_now)

    def add_message(self, message: ConversationMessage) -> None:
        """Add a message to the session.

        Args:
            message: Message to add.
        """
        self.messages.append(message)
        self.last_activity_at = _utc_now()

    def get_history(self, limit: int = 20) -> list[ConversationMessage]:
        """Get conversation history with limit.

        Args:
            limit: Maximum number of messages to return.

        Returns:
            List of messages, most recent first.
        """
        return self.messages[-limit:]

    def is_expired(self, timeout_seconds: int | None = None) -> bool:
        """Check if session is expired.

        Args:
            timeout_seconds: Timeout in seconds. Uses config default if None.

        Returns:
            True if session is expired, False otherwise.
        """
        if timeout_seconds is None:
            timeout_seconds = settings.session.timeout_seconds
        delta = _utc_now() - self.last_activity_at
        return delta.total_seconds() > timeout_seconds
