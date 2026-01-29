# Delta Spec: c002-data-contracts

**File**: `specs/pydantic-zod-sync/spec.md`

**Generated**: 2026-01-29
**Change**: c002-data-contracts
**Related**: c010-voice-client

---

## ADDED Requirements

### Requirement: Voice Streaming Data Contracts

The Pydantic ↔ Zod synchronization MUST include voice streaming data contracts for kyutai protocol integration.

#### Scenario: Kyutai protocol contracts exist

- **WHEN** c010-voice-client is implemented
- **THEN** application/dtos/voice_gateway_dtos.py exists with KyutaiMessage Pydantic model
- **AND** types/voice-protocol.ts exists with KyutaiMessage Zod schema
- **AND** field aliases map snake_case → camelCase (sessionId, messageId, etc.)
- **AND** KyutaiMessageType enum values match exactly
- **AND** ConversationSession, ConversationMessage models have Pydantic ↔ Zod parity

#### Scenario: Conversational state contracts exist

- **WHEN** c010-voice-client is implemented
- **THEN** domain/entities/conversation_session.py has ConversationSession entity
- **AND** types/voice-protocol.ts has ConversationSession Zod schema
- **AND** MessageRole enum values match exactly (user, assistant, system)
- **AND** ConversationContext model has Pydantic ↔ Zod parity

---

**Related Changes**:
- c010-voice-client - Voice streaming data contracts implementation
