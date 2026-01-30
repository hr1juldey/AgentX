# Spec: pydantic-zod-sync

**File**: `specs/pydantic-zod-sync/spec.md`

## 1.1 Purpose

Define the synchronization mechanism between backend Pydantic v2 models and frontend Zod schemas, ensuring single source of truth and type safety across the stack.

## 1.2 Scope

**In Scope**:
- Pydantic v2 model definitions (backend)
- Zod schema definitions (frontend)
- Type mapping rules (Python → TypeScript)
- Field alias handling
- Validation parity

**Out of Scope**:
- UI descriptor contracts (see ui-descriptor-contracts spec)
- WebSocket protocol (see websocket-protocol spec)
- LangGraph server protocol (see C003-agent-pipeline)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PZ-001 | Pydantic models SHALL use v2 syntax with `pydantic.BaseModel` | Must |
| FR-PZ-002 | Zod schemas SHALL match Pydantic models field-by-field | Must |
| FR-PZ-003 | Field names SHALL use alias mapping for snake_case → camelCase | Must |
| FR-PZ-004 | Optional fields SHALL be optional in both Pydantic and Zod | Must |
| FR-PZ-005 | Enum values SHALL match exactly (case-sensitive) | Must |
| FR-PZ-006 | Nested objects SHALL be recursively mapped | Must |
| FR-PZ-007 | Array types SHALL map `list[T]` → `z.array(TSchema)` | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PZ-001 | Type checking on both ends (tsc --noEmit, pyright) | Must |
| NFR-PZ-002 | Runtime validation (Pydantic, Zod) | Must |
| NFR-PZ-003 | Single source of truth (LLD locks definitions) | Must |
| NFR-PZ-004 | Automated sync verification (CI check) | Should |

## 1.4 Data Model

### Type Mapping Table

| Python Type | Pydantic Field | TypeScript Type | Zod Schema | Notes |
|-------------|---------------|-----------------|------------|-------|
| `str` | `Field()` | `string` | `z.string()` | Direct mapping |
| `int` | `Field()` | `number` | `z.number()` | JS has no int/float distinction |
| `float` | `Field()` | `number` | `z.number()` | - |
| `bool` | `Field()` | `boolean` | `z.boolean()` | - |
| `list[T]` | `Field(default_factory=list)` | `T[]` | `z.array(TSchema)` | Recursive for nested objects |
| `dict[str, T]` | `Field(default_factory=dict)` | `Record<string, T>` | `z.record(z.unknown())` | Use `z.record(TSchema)` for uniform types |
| `T \| None` | `Field(default=None)` | `T \| undefined` | `TSchema.optional()` | Optional fields |
| `Optional[T]` | `Field(default=None)` | `T \| null` | `TSchema.nullable()` | Explicit null handling |
| `datetime` | `Field()` | `string` (ISO 8601) | `z.string().datetime()` | Serialize as ISO string |
| `UUID` | `Field()` | `string` | `z.string().uuid()` | Serialize as string |
| `Enum` | `enum.Enum` | `enum` | `z.enum([...])` | Values must match exactly |

### Field Alias Mapping

**Backend (Pydantic v2)**:
```python
from pydantic import BaseModel, Field

class SearchRequest(BaseModel):
    query: str = Field(alias="q")  # Backend: query, Frontend: q
    max_hops: int = Field(default=3, alias="maxHops")
    device_context: str = Field(default="desktop", alias="deviceContext")

    class Config:
        populate_by_name = True  # Allow both alias and field name
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

export const SearchRequestSchema = z.object({
  q: z.string(),  // Matches alias
  maxHops: z.number().default(3),  // camelCase
  deviceContext: z.string().default("desktop"),
});

export type SearchRequest = z.infer<typeof SearchRequestSchema>;
```

### Complex Nested Example

**Backend (Pydantic v2)**:
```python
from pydantic import BaseModel, Field
from typing import Any, Dict

class CardAction(BaseModel):
    label: str
    action: str
    variant: str = Field(default="outline")

class CardDescriptor(BaseModel):
    descriptor_id: str = Field(alias="id")
    descriptor_type: str = Field(alias="type")
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    actions: list[CardAction] = Field(default_factory=list)

    class Config:
        populate_by_name = True
```

**Frontend (Zod)**:
```typescript
import { z } from 'zod';

export const CardActionSchema = z.object({
  label: z.string(),
  action: z.string(),
  variant: z.string().default("outline"),
});

export const CardDescriptorSchema = z.object({
  id: z.string(),
  type: z.string(),
  title: z.string(),
  content: z.string(),
  metadata: z.record(z.unknown()).default({}),
  actions: z.array(CardActionSchema).default([]),
});

export type CardDescriptor = z.infer<typeof CardDescriptorSchema>;
```

## 1.5 API Contract

### Sync Verification

**CI Check** (add to pipeline):
```bash
# Backend: Verify Pydantic models
python -m py_compile agentx/ui/descriptors/*.py

# Frontend: Verify Zod schemas
npx tsc --noEmit

# Manual: Compare enum values
python scripts/sync_enums.py  # Custom script to verify enum parity
```

**Verification Script** (scripts/sync_enums.py):
```python
#!/usr/bin/env python3
"""Verify Pydantic enums match Zod enums exactly."""

import re
from pathlib import Path

def extract_zod_enum_typescript(file_path: Path) -> set[str]:
    """Extract enum values from Zod schema."""
    content = file_path.read_text()
    match = re.search(r'z\.enum\(\[(.*?)\]\)', content, re.DOTALL)
    if match:
        values = match.group(1)
        return {v.strip().strip('"\'') for v in values.split(',')}
    return set()

def extract_pydantic_enum_python(file_path: Path) -> set[str]:
    """Extract enum values from Pydantic model."""
    content = file_path.read_text()
    # Find Enum class and extract values
    match = re.search(r'class (\w+)\(str, Enum\):.*?"""(.*?)"""(.*?)(?=\nclass|\Z)', content, re.DOTALL)
    if match:
        values = re.findall(r'(\w+)\s*=\s*["\']([^"\']+)["\']', content)
        return {value for _, value in values}
    return set()

def main():
    backend_dir = Path("agentx/ui/descriptors")
    frontend_dir = Path("frontend/types")

    # Compare WidgetType enums
    backend_enum = extract_pydantic_enum_python(backend_dir / "base.py")
    frontend_enum = extract_zod_enum_typescript(frontend_dir / "descriptors.ts")

    if backend_enum != frontend_enum:
        print(f"ERROR: Enum mismatch!")
        print(f"  Backend: {backend_enum}")
        print(f"  Frontend: {frontend_enum}")
        return 1

    print("✓ All enums synchronized")
    return 0

if __name__ == "__main__":
    exit(main())
```

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-PZ-001 | Field names use camelCase on frontend | Code review, linter |
| BR-PZ-002 | Field names use snake_case on backend | Code review, ruff |
| BR-PZ-003 | Aliases map backend → frontend names | Pydantic Field(alias=...) |
| BR-PZ-004 | Enum values match exactly (case-sensitive) | CI verification script |
| BR-PZ-005 | Optional fields use `.optional()` in Zod | Code review |
| BR-PZ-006 | Nested objects use recursive mapping | Code review |

## 1.7 Acceptance Criteria

- [ ] All Pydantic models have corresponding Zod schemas
- [ ] Field aliases map snake_case → camelCase
- [ ] Enum values match exactly
- [ ] Optional fields consistent across both
- [ ] Nested objects recursively mapped
- [ ] CI verification script passes
- [ ] Type checking passes (tsc --noEmit, pyright)

## 1.8 Type Sync Checklist

For each Pydantic model, verify:

| Check | Description | Status |
|-------|-------------|--------|
| Field names | camelCase in Zod, snake_case in Pydantic | ☐ |
| Field aliases | `Field(alias=...)` in Pydantic | ☐ |
| Optional fields | `.optional()` in Zod, `default=None` in Pydantic | ☐ |
| Enum values | Exact match (case-sensitive) | ☐ |
| Array types | `z.array(...)` for `list[...]` | ☐ |
| Dict types | `z.record(...)` for `dict[str, ...]` | ☐ |
| Nested objects | Recursive schema definitions | ☐ |

---

## 1.9 ADDED Requirements (from C010 voice-client)

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

## 2.0 MODIFIED Requirements (from C010 voice-client)

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

### Data Model: Kyutai Protocol Pydantic Models

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

### Data Model: Voice Protocol Zod Schemas

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

### Type Sync Checklist for Kyutai Protocol

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
- C010 voice-client - VoiceGatewayService data contracts
- `voice-gateway` spec - Voice gateway service data contracts
- `conversational-state` spec - Conversational state data contracts
- `websocket-protocol` spec - Kyutai protocol message types

---

