"""WebSocket message protocols for Real AgentX v0.1.

This module provides message schemas for bidirectional WebSocket communication.
Supports real-time streaming of agent responses and UI components.

This module re-exports all message classes from split components for backward compatibility.
"""

# Base classes
from agentx.ui.protocols.messages.base import WebSocketMessage

# Enums
from agentx.ui.protocols.messages.enums import MessageType

# Client -> Server messages
from agentx.ui.protocols.messages.client import (
    InterruptMessage,
    PingMessage,
    QueryMessage,
)

# Voice messages
from agentx.ui.protocols.messages.voice import VoiceDataMessage

# Server -> Client messages
from agentx.ui.protocols.messages.server import (
    ResponseMessage,
    ToolCallMessage,
    UIComponentMessage,
)

# System messages
from agentx.ui.protocols.messages.system import (
    ErrorMessage,
    PongMessage,
    StatusMessage,
)

__all__ = [
    # Base
    "WebSocketMessage",
    # Enums
    "MessageType",
    # Client -> Server
    "QueryMessage",
    "InterruptMessage",
    "PingMessage",
    # Voice
    "VoiceDataMessage",
    # Server -> Client
    "ResponseMessage",
    "UIComponentMessage",
    "ToolCallMessage",
    # System
    "ErrorMessage",
    "StatusMessage",
    "PongMessage",
]
