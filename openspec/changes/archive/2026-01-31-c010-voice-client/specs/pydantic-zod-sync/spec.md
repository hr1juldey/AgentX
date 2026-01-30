# Delta Spec: pydantic-zod-sync

**File**: `specs/pydantic-zod-sync/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## ADDED Requirements

### Requirement: Kyutai Protocol Data Contracts

The system SHALL provide Pydantic models and Zod schemas for kyutai voice-server WebSocket protocol messages.

#### Scenario: KyutaiMessage Pydantic model

- **WHEN** VoiceGatewayService processes kyutai WebSocket message
- **THEN** KyutaiMessage Pydantic model validates message structure
- **AND** model includes: type (KyutaiMessageType), data (Any), session_id (str), timestamp (float), metadata (Optional[Dict])
- **AND** model provides to_json() and from_json() methods

#### Scenario: KyutaiMessageType enum

- **WHEN** KyutaiMessage is created or validated
- **THEN** KyutaiMessageType enum validates message type
- **AND** enum values: CONFIG, AUDIO, TEXT, ERROR, EOS, HEARTBEAT
- **AND** enum values match kyutai protocol exactly (case-sensitive)

#### Scenario: ConversationSession Pydantic model

- **WHEN** ConversationStateManager tracks session
- **THEN** ConversationSession Pydantic model validates session structure
- **AND** model includes: session_id (UUID), messages (list[ConversationMessage]), context (ConversationContext), created_at (datetime), last_activity_at (datetime)

#### Scenario: ConversationMessage Pydantic model

- **WHEN** ConversationStateManager adds message
- **THEN** ConversationMessage Pydantic model validates message structure
- **AND** model includes: message_id (UUID), role (MessageRole), content (str), timestamp (datetime), metadata (Optional[Dict])

#### Scenario: MessageRole enum

- **WHEN** ConversationMessage is created or validated
- **THEN** MessageRole enum validates message role
- **AND** enum values: USER, ASSISTANT, SYSTEM
- **AND** enum values match across Pydantic and Zod

#### Scenario: KyutaiMessage Zod schema

- **WHEN** VoiceClient processes WebSocket message in frontend
- **THEN** KyutaiMessage Zod schema validates message structure
- **AND** schema matches Pydantic model field-by-field
- **AND** schema uses camelCase for field names (sessionId, not session_id)

#### Scenario: ConversationMessage Zod schema

- **WHEN** Frontend displays conversation history
- **THEN** ConversationMessage Zod schema validates message structure
- **AND** schema matches Pydantic model field-by-field
- **AND** optional fields use .optional() in Zod

---

## MODIFIED Requirements

### Requirement: Voice Streaming Data Contracts

The data contracts for voice streaming SHALL be extended to support kyutai protocol messages and conversational state.

#### Scenario: Pydantic models for voice gateway

- **WHEN** VoiceGatewayService processes voice messages
- **THEN** all Pydantic models use v2 syntax with pydantic.BaseModel
- **AND** all Pydantic models use Field aliases for snake_case → camelCase
- **AND** all Pydantic models pass ruff check and pyrefly type checking

#### Scenario: Zod schemas for voice client

- **WHEN** VoiceClient processes voice messages
- **THEN** all Zod schemas match Pydantic models field-by-field
- **AND** all Zod schemas use camelCase for field names
- **AND** all Zod schemas pass TypeScript type checking (tsc --noEmit)

---

**Data Model: Kyutai Protocol Pydantic Models**

**File: agentx/application/dtos/voice_gateway_dtos.py**

```python
"""Voice gateway DTOs for kyutai protocol integration."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID
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
    session_id: str = Field(..., alias="session_id")
    timestamp: float
    metadata: dict[str, Any] | None = None

    class Config:
        populate_by_name = True

    def to_json(self) -> str:
        """Convert to JSON string."""
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

    class Config:
        populate_by_name = True


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

    class Config:
        populate_by_name = True


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
    messages: list[ConversationMessageDTO] = Field(default_factory=list, alias="messages")
    context: ConversationContextDTO = Field(default_factory=ConversationContextDTO, alias="context")
    created_at: datetime = Field(..., alias="createdAt")
    last_activity_at: datetime = Field(..., alias="lastActivityAt")

    class Config:
        populate_by_name = True
```

---

**Data Model: Voice Protocol Zod Schemas**

**File: frontend/types/voice-protocol.ts**

```typescript
import { z } from 'zod';

/**
 * Kyutai WebSocket message types.
 */
export const KyutaiMessageType = z.enum([
  'Config',
  'Audio',
  'Text',
  'Error',
  'Eos',
  'Heartbeat',
]);

export type KyutaiMessageType = z.infer<typeof KyutaiMessageType>;

/**
 * Kyutai WebSocket message schema.
 */
export const KyutaiMessageSchema = z.object({
  type: KyutaiMessageType,
  data: z.unknown(),
  sessionId: z.string(),
  timestamp: z.number(),
  metadata: z.record(z.unknown()).optional(),
});

export type KyutaiMessage = z.infer<typeof KyutaiMessageSchema>;

/**
 * Message role in conversation.
 */
export const MessageRole = z.enum([
  'user',
  'assistant',
  'system',
]);

export type MessageRole = z.infer<typeof MessageRole>;

/**
 * Conversation message schema.
 */
export const ConversationMessageSchema = z.object({
  messageId: z.string(),
  role: MessageRole,
  content: z.string(),
  timestamp: z.string().datetime(),
  metadata: z.record(z.unknown()).optional(),
});

export type ConversationMessage = z.infer<typeof ConversationMessageSchema>;

/**
 * Conversation context schema.
 */
export const ConversationContextSchema = z.object({
  currentTopic: z.string().optional(),
  entities: z.record(z.unknown()).optional(),
  sentiment: z.string().optional(),
  language: z.string().default('en'),
  timezone: z.string().default('UTC'),
});

export type ConversationContext = z.infer<typeof ConversationContextSchema>;

/**
 * Conversation session schema.
 */
export const ConversationSessionSchema = z.object({
  sessionId: z.string(),
  messages: z.array(ConversationMessageSchema).default([]),
  context: ConversationContextSchema.default({
    language: 'en',
    timezone: 'UTC',
  }),
  createdAt: z.string().datetime(),
  lastActivityAt: z.string().datetime(),
});

export type ConversationSession = z.infer<typeof ConversationSessionSchema>;
```

---

**Type Sync Checklist for Kyutai Protocol**

| Check | Description | Status |
|-------|-------------|--------|
| KyutaiMessage | Pydantic + Zod schemas match | ☐ |
| KyutaiMessageType | Enum values match exactly | ☐ |
| ConversationMessage | Pydantic + Zod schemas match | ☐ |
| MessageRole | Enum values match exactly | ☐ |
| ConversationContext | Pydantic + Zod schemas match | ☐ |
| ConversationSession | Pydantic + Zod schemas match | ☐ |
| Field aliases | sessionId, messageId, etc. mapped | ☐ |
| Optional fields | .optional() in Zod, default=None in Pydantic | ☐ |

---

**Related Changes**:
- `voice-gateway` spec - VoiceGatewayService data contracts
- `conversational-state` spec - Conversational state data contracts
- `websocket-protocol` delta spec - Kyutai protocol message types

---
