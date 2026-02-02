"""Base WebSocket message class.

Provides the foundation for all WebSocket message types.
"""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from agentx.ui.protocols.messages.enums import MessageType


@dataclass
class WebSocketMessage:
    """Base WebSocket message class.

    All message types inherit from this class.
    Provides common fields and serialization methods.
    """

    message_id: UUID = field(default_factory=uuid4)
    message_type: MessageType = field(default=MessageType.STATUS)
    session_id: UUID | None = None
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary for serialization.

        Returns:
            dict: Serializable message representation.
        """
        return {
            "message_id": str(self.message_id),
            "message_type": self.message_type.value,
            "session_id": str(self.session_id) if self.session_id else None,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WebSocketMessage":
        """Create message from dictionary.

        Args:
            data: Deserialized message data.

        Returns:
            WebSocketMessage: Message instance.
        """
        return cls(
            message_id=UUID(data["message_id"]) if "message_id" in data else uuid4(),
            message_type=MessageType(
                data.get("message_type", MessageType.STATUS.value)
            ),
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
            timestamp=float(data.get("timestamp", __import__("time").time())),  # type: ignore[arg-type]
            data=data.get("data", {}),
        )
