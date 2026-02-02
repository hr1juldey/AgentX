"""System and status WebSocket messages.

Messages for system-level communication and connection lifecycle.
"""

from dataclasses import dataclass
from typing import override

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


@dataclass
class ErrorMessage(WebSocketMessage):
    """Error message.

    Notifies client of errors during processing.
    """

    @override
    def __init__(self, error_message: str, error_code: str | None = None):
        """Initialize error message.

        Args:
            error_message: Human-readable error message.
            error_code: Optional machine-readable error code.
        """
        super().__init__(
            message_type=MessageType.ERROR,
            data={
                "error_message": error_message,
                "error_code": error_code,
            },
        )


@dataclass
class StatusMessage(WebSocketMessage):
    """Status message for connection state.

    Used for connection lifecycle events.
    """

    @override
    def __init__(self, status: str, details: str | None = None):
        """Initialize status message.

        Args:
            status: Status value (connecting, connected, disconnected).
            details: Optional status details.
        """
        super().__init__(
            message_type=MessageType.STATUS,
            data={
                "status": status,
                "details": details,
            },
        )


@dataclass
class PongMessage(WebSocketMessage):
    """Pong message for connection health check.

    Sent from server in response to ping messages.
    """

    @override
    def __init__(self):
        """Initialize pong message."""
        super().__init__(
            message_type=MessageType.PONG,
            data={},
        )
