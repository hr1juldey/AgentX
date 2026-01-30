# Delta Spec: websocket-protocol

**File**: `specs/websocket-protocol/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## ADDED Requirements

### Requirement: Kyutai Protocol Message Types

The system SHALL support kyutai voice-server WebSocket message types for external voice service integration.

#### Scenario: Config message to kyutai

- **WHEN** VoiceGatewayService connects to kyutai STT or TTS endpoint
- **THEN** system sends Config message with format settings
- **AND** message structure matches kyutai protocol exactly
- **AND** message includes: type="Config", data={config}, session_id, timestamp

#### Scenario: Audio message to kyutai STT

- **WHEN** frontend sends audio chunk to AgentX
- **THEN** VoiceGatewayService routes Audio message to kyutai STT endpoint
- **AND** message includes: type="Audio", data="base64_audio", session_id, timestamp
- **AND** kyutai STT processes audio and returns Text message

#### Scenario: Text message from kyutai STT

- **WHEN** kyutai STT transcribes audio
- **THEN** VoiceGatewayService receives Text message
- **AND** message includes: type="Text", data="transcript_text", session_id, timestamp
- **AND** VoiceGatewayService routes transcript to frontend and agent pipeline

#### Scenario: Text message to kyutai TTS

- **WHEN** agent pipeline generates response
- **THEN** VoiceGatewayService sends Text message to kyutai TTS endpoint
- **AND** message includes: type="Text", data="response_text", session_id, timestamp
- **AND** kyutai TTS synthesizes text and returns Audio message

#### Scenario: Audio message from kyutai TTS

- **WHEN** kyutai TTS synthesizes text
- **THEN** VoiceGatewayService receives Audio message
- **AND** message includes: type="Audio", data="base64_audio", session_id, timestamp
- **AND** VoiceGatewayService routes audio chunks to frontend

#### Scenario: Error message from kyutai

- **WHEN** kyutai server encounters error
- **THEN** VoiceGatewayService receives Error message
- **AND** message includes: type="Error", data="error_message", session_id, timestamp
- **AND** VoiceGatewayService translates error to frontend format

#### Scenario: Eos message from kyutai

- **WHEN** kyutai STT completes transcription
- **THEN** VoiceGatewayService receives Eos message
- **AND** message includes: type="Eos", data=null, session_id, timestamp
- **AND** VoiceGatewayService flushes transcript buffer and sends to frontend

#### Scenario: Heartbeat message to kyutai

- **WHEN** VoiceGatewayService maintains connection to kyutai
- **THEN** system sends periodic Heartbeat messages
- **AND** message includes: type="Heartbeat", data=null, session_id, timestamp
- **AND** kyutai responds with Heartbeat acknowledgment

### Requirement: Conversational State Messages

The system SHALL support conversational state messages for tracking conversation history and context.

#### Scenario: ConversationHistory message

- **WHEN** frontend requests conversation history
- **THEN** system returns ConversationHistory message
- **AND** message includes: messages=[{role, content, timestamp}], session_id
- **AND** frontend displays conversation history in UI

#### Scenario: ContextUpdate message

- **WHEN** agent pipeline extracts context entities
- **THEN** system emits ContextUpdate message
- **AND** message includes: context={topic, entities, sentiment}, session_id
- **AND** ConversationStateManager updates session context

### Requirement: Interrupt Message Type

The system SHALL support interrupt messages for stopping TTS playback.

#### Scenario: Interrupt from frontend

- **WHEN** user presses "Stop" button during TTS playback
- **THEN** frontend sends Interrupt message to AgentX
- **AND** message includes: type="Interrupt", data="interrupt", session_id
- **AND** VoiceGatewayService sets session.interrupted flag
- **AND** TextStreamHandler stops TTS streaming
- **AND** VoiceGatewayService closes kyutai TTS WebSocket connection

---

## MODIFIED Requirements

### Requirement: WebSocket Message Format

The WebSocket message format MUST align with kyutai voice-server protocol for external service integration.

#### Scenario: Kyutai protocol message format

- **WHEN** VoiceGatewayService sends message to kyutai server
- **THEN** message format matches kyutai protocol exactly
- **AND** message structure: {type, data, session_id, timestamp, metadata?}
- **AND** type values: "Config", "Audio", "Text", "Error", "Eos", "Heartbeat"
- **AND** session_id is UUID string
- **AND** timestamp is Unix timestamp (float seconds)

#### Scenario: Frontend WebSocket message format

- **WHEN** frontend sends message to AgentX
- **THEN** message format matches kyutai protocol for consistency
- **AND** message structure: {type, data, session_id, timestamp}
- **AND** VoiceGatewayService can route message to kyutai directly

---

**Related Changes**:
- `voice-gateway` spec - VoiceGatewayService for message routing
- `conversational-state` spec - Conversational state messages
- `voice-client` spec - Frontend WebSocket client
- `pydantic-zod-sync` delta spec - Pydantic models for kyutai protocol

---
