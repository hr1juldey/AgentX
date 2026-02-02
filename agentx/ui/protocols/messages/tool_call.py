"""Tool call message for server-to-client communication.

Notifies client of tool execution in progress.
"""

from dataclasses import dataclass
from typing import Any, override
from uuid import UUID, uuid4

from agentx.ui.protocols.messages.base import WebSocketMessage
from agentx.ui.protocols.messages.enums import MessageType


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
