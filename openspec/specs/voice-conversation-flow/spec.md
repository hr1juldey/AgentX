# Spec: Voice Conversation Flow

End-to-end voice interaction pipeline from WebSocket to agent response.

## Purpose

Handle complete voice interaction sessions including WebSocket connection management, STT audio buffering, agent query execution with memory, and TTS audio synthesis.

## Requirements

### Requirement: WebSocket voice session handling
The system SHALL accept WebSocket connections for voice sessions and handle the full STT → Agent → TTS pipeline.

#### Scenario: Successful voice session
- **WHEN** client connects to `/ws/voice?session_id={uuid}`
- **THEN** system accepts connection and creates session state

#### Scenario: Session ID is required
- **WHEN** client connects without session_id parameter
- **THEN** system returns 400 Bad Request error

---

### Requirement: STT audio message handling
The system SHALL receive audio messages from STT service and buffer them until Eos (End of Stream).

#### Scenario: Audio message buffering
- **WHEN** client sends Audio message with base64-encoded audio data
- **THEN** system appends audio to session buffer

#### Scenario: Eos triggers transcription
- **WHEN** client sends Eos message
- **THEN** system sends buffered audio to STT service for transcription

---

### Requirement: Agent query execution with memory
The system SHALL execute agent query with memory context and return response.

#### Scenario: Query with memory context
- **WHEN** STT transcription is complete
- **THEN** system searches Mem0AI for relevant context
- **AND** system executes agent with question + memory context + DSPy history
- **AND** system returns agent response

#### Scenario: Mem0AI unavailable fallback
- **WHEN** Mem0AI service is unavailable
- **THEN** system logs warning and continues without memory context
- **AND** system does not fail the query

---

### Requirement: TTS audio synthesis
The system SHALL send agent response to TTS service for audio synthesis.

#### Scenario: Text to speech conversion
- **WHEN** agent returns text response
- **THEN** system sends text to TTS service
- **AND** system streams audio chunks to client as they arrive

#### Scenario: TTS preprocessing
- **WHEN** sending text to TTS service
- **THEN** system applies text preprocessing (punctuation, sentence breaks)
- **AND** system formats for natural speech

---

### Requirement: Session state management
The system SHALL maintain session state including DSPy history and metadata.

#### Scenario: Session creation
- **WHEN** WebSocket connects with new session_id
- **THEN** system creates new session with empty DSPy history
- **AND** system initializes session metadata (start time, user_id)

#### Scenario: Session reconnection
- **WHEN** WebSocket connects with existing session_id
- **THEN** system loads existing session state including DSPy history
- **AND** system continues conversation with preserved context

#### Scenario: Session cleanup on disconnect
- **WHEN** WebSocket disconnects
- **THEN** system saves final state to Mem0AI
- **AND** system cleans up in-memory session state after timeout

---

### Requirement: Error handling and recovery
The system SHALL handle errors gracefully and provide meaningful error messages.

#### Scenario: STT service error
- **WHEN** STT service returns error
- **THEN** system sends Error message to client with error details
- **AND** system keeps session open for retry

#### Scenario: Agent execution error
- **WHEN** agent execution fails
- **THEN** system sends Error message to client
- **AND** system logs error with stack trace

#### Scenario: TTS service error
- **WHEN** TTS service returns error
- **THEN** system falls back to sending text response only
- **AND** system logs warning about TTS failure
