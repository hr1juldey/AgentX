"""Client-to-server WebSocket messages.

Messages sent from the frontend to the backend.
"""

from dataclasses import dataclass
from typing import override
from uuid import UUID

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


@dataclass
class QueryMessage(WebSocketMessage):
    """Client query message.

    Sent from client to initiate agent processing.
    """

    @override
    def __init__(self, query: str, session_id: UUID | None = None):
        """Initialize query message.

        Args:
            query: User's query text.
            session_id: Optional session ID for continuation.
        """
        super().__init__(
            message_type=MessageType.QUERY,
            session_id=session_id,
            data={"query": query},
        )


@dataclass
class InterruptMessage(WebSocketMessage):
    """Interrupt message.

    Sent from client to interrupt current agent processing.
    """

    @override
    def __init__(self, session_id: UUID):
        """Initialize interrupt message.

        Args:
            session_id: Session identifier.
        """
        super().__init__(
            message_type=MessageType.INTERRUPT,
            session_id=session_id,
            data={},
        )


@dataclass
class PingMessage(WebSocketMessage):
    """Ping message for connection health check.

    Sent from client to verify server responsiveness.
    """

    @override
    def __init__(self):
        """Initialize ping message."""
        super().__init__(
            message_type=MessageType.PING,
            data={},
        )
