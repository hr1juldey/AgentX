"""Voice gateway DTOs for kyutai protocol integration."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class KyutaiMessageType(str, Enum):
    """Kyutai WebSocket message types."""

    CONFIG = "Config"
    AUDIO = "Audio"
    TEXT = "Text"
    ERROR = "Error"
    EOS = "Eos"
    HEARTBEAT = "Heartbeat"


class KyutaiMessage(BaseModel):
    """Kyutai WebSocket message.

    Attributes:
        type: Message type (Config, Audio, Text, Error, Eos, Heartbeat).
        data: Message data (base64 audio for Audio, text for Text, etc.).
        session_id: Session identifier.
        timestamp: Unix timestamp (seconds since epoch).
        metadata: Optional metadata.
    """

    type: KyutaiMessageType
    data: Any
    session_id: str = Field(..., alias="sessionId")
    timestamp: float
    metadata: dict[str, Any] | None = None

    model_config = {"populate_by_name": True}

    def to_json(self) -> str:
        """Convert to JSON string with camelCase keys."""
        import json

        return json.dumps(self.model_dump(by_alias=True))

    @classmethod
    def from_json(cls, json_str: str) -> "KyutaiMessage":
        """Create from JSON string."""
        import json

        data = json.loads(json_str)
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with camelCase keys."""
        return self.model_dump(by_alias=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KyutaiMessage":
        """Create from dictionary."""
        return cls(**data)


class MessageRole(str, Enum):
    """Message role in conversation."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationMessageDTO(BaseModel):
    """Conversation message DTO.

    Attributes:
        message_id: Unique message identifier.
        role: Message role (user, assistant, system).
        content: Message content.
        timestamp: Message timestamp.
        metadata: Optional metadata.
    """

    message_id: str = Field(..., alias="messageId")
    role: MessageRole
    content: str
    timestamp: datetime
    metadata: dict[str, Any] | None = Field(None, alias="metadata")

    model_config = {"populate_by_name": True}


class ConversationContextDTO(BaseModel):
    """Conversation context DTO.

    Attributes:
        current_topic: Current conversation topic.
        entities: Extracted entities.
        sentiment: Conversation sentiment.
        language: Conversation language.
        timezone: User timezone.
    """

    current_topic: str | None = Field(None, alias="currentTopic")
    entities: dict[str, Any] | None = Field(None, alias="entities")
    sentiment: str | None = Field(None, alias="sentiment")
    language: str = Field("en", alias="language")
    timezone: str = Field("UTC", alias="timezone")

    model_config = {"populate_by_name": True}


class ConversationSessionDTO(BaseModel):
    """Conversation session DTO.

    Attributes:
        session_id: Session identifier.
        messages: List of messages.
        context: Conversation context.
        created_at: Creation timestamp.
        last_activity_at: Last activity timestamp.
    """

    session_id: str = Field(..., alias="sessionId")
    messages: list[ConversationMessageDTO] = Field(
        default_factory=list, alias="messages"
    )
    context: ConversationContextDTO = Field(
        default_factory=ConversationContextDTO, alias="context"
    )
    created_at: datetime = Field(..., alias="createdAt")
    last_activity_at: datetime = Field(..., alias="lastActivityAt")

    model_config = {"populate_by_name": True}
