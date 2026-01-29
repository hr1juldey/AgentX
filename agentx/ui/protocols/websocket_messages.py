"""WebSocket message protocols for Real AgentX v0.1.

Defines message schemas for bidirectional WebSocket communication.
Supports real-time streaming of agent responses and UI components.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, override
from uuid import UUID, uuid4


class MessageType(str, Enum):
    """WebSocket message types."""

    # Client -> Server
    QUERY = "query"
    VOICE_DATA = "voice_data"
    INTERRUPT = "interrupt"
    PING = "ping"

    # Server -> Client
    RESPONSE = "response"
    REASONING = "reasoning"
    UI_COMPONENT = "ui_component"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    ERROR = "error"
    PONG = "pong"
    STATUS = "status"


@dataclass
class WebSocketMessage:
    """Base WebSocket message class."""

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
            timestamp=data.get("timestamp", __import__("time").time()),
            data=data.get("data", {}),
        )


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
class VoiceDataMessage(WebSocketMessage):
    """Voice data message for streaming audio.

    Sent from client for STT processing.
    """

    @override
    def __init__(self, audio_data: bytes, session_id: UUID, sample_rate: int = 16000):
        """Initialize voice data message.

        Args:
            audio_data: Raw audio bytes.
            session_id: Session identifier.
            sample_rate: Audio sample rate.
        """
        # Store audio data as base64 for JSON serialization
        import base64

        super().__init__(
            message_type=MessageType.VOICE_DATA,
            session_id=session_id,
            data={
                "audio_data": base64.b64encode(audio_data).decode(),
                "sample_rate": sample_rate,
            },
        )


@dataclass
class ResponseMessage(WebSocketMessage):
    """Agent response message.

    Streams agent response text to client.
    """

    @override
    def __init__(
        self,
        content: str,
        session_id: UUID,
        is_complete: bool = False,
        is_delta: bool = False,
    ):
        """Initialize response message.

        Args:
            content: Response text content.
            session_id: Session identifier.
            is_complete: Whether this is the final message.
            is_delta: Whether this is a streaming delta.
        """
        super().__init__(
            message_type=MessageType.RESPONSE,
            session_id=session_id,
            data={
                "content": content,
                "is_complete": is_complete,
                "is_delta": is_delta,
            },
        )


@dataclass
class UIComponentMessage(WebSocketMessage):
    """UI component message for server-driven UI.

    Emits UI component descriptors to frontend for rendering.
    Pattern from C007: LangGraph server-driven UI.
    """

    @override
    def __init__(
        self,
        component_type: str,
        props: dict[str, Any],
        session_id: UUID,
        merge: bool = False,
        component_id: UUID | None = None,
    ):
        """Initialize UI component message.

        Args:
            component_type: Type of UI component.
            props: Component properties.
            session_id: Session identifier.
            merge: Whether to merge with existing component.
            component_id: Optional component ID for merging.
        """
        super().__init__(
            message_type=MessageType.UI_COMPONENT,
            session_id=session_id,
            data={
                "component_type": component_type,
                "props": props,
                "merge": merge,
                "component_id": str(component_id) if component_id else str(uuid4()),
            },
        )


@dataclass
class ToolCallMessage(WebSocketMessage):
    """Tool call message.

    Notifies client of tool execution in progress.
    """

    @override
    def __init__(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        session_id: UUID,
        call_id: UUID | None = None,
    ):
        """Initialize tool call message.

        Args:
            tool_name: Name of the tool being called.
            parameters: Tool parameters.
            session_id: Session identifier.
            call_id: Optional call identifier.
        """
        super().__init__(
            message_type=MessageType.TOOL_CALL,
            session_id=session_id,
            data={
                "tool_name": tool_name,
                "parameters": parameters,
                "call_id": str(call_id) if call_id else str(uuid4()),
            },
        )


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
