"""Domain enums for Real AgentX v0.1.

Defines all enumeration types used across the domain layer.
Locked from LLD: docs/engineering/lld/domain_model.md
"""

from enum import Enum


class SessionState(str, Enum):
    """Agent session lifecycle states.

    Follows state machine pattern from LLD.
    """

    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ERROR = "error"


class UIComponentType(str, Enum):
    """UI component/descriptor types.

    Maps to frontend React components via LangGraph.
    """

    MARKDOWN = "markdown"
    CARD = "card"
    FORM = "form"
    PROGRESS = "progress"
    ACTION = "action"
    CONFIRMATION = "confirmation"
    VOICE = "voice"
    IMAGE = "image"
    GALLERY = "gallery"
    CHART = "chart"
    SEARCH_RESULT = "search_result"
    HOP_PROGRESS = "hop_progress"
    CITATION_CARD = "citation_card"


class MessageRole(str, Enum):
    """Message roles in agent conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolStatus(str, Enum):
    """Tool execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class MemoryType(str, Enum):
    """Memory storage types."""

    EPISODIC = "episodic"  # Conversation history
    SEMANTIC = "semantic"  # Vector embeddings
    PROCEDURAL = "procedural"  # User preferences
