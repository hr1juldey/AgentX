"""Response message for server-to-client communication.

Streams agent response text to client.
"""

from dataclasses import dataclass
from typing import override
from uuid import UUID

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


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
