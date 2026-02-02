"""WebSocket message type enums.

Defines message types for bidirectional WebSocket communication.
"""

from enum import Enum


class MessageType(str, Enum):
    """WebSocket message types.

    Categorizes messages by direction and purpose:
    - Client -> Server: QUERY, VOICE_DATA, INTERRUPT, PING
    - Server -> Client: RESPONSE, REASONING, UI_COMPONENT, TOOL_CALL, TOOL_RESULT, ERROR, PONG, STATUS
    """

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
