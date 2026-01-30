# Proposal: c010-voice-client

**Generated**: 2026-01-29
**Change**: c010-voice-client
**Schema**: spec-driven v1

---

## Why

Current c004-voice-streaming treats voice services (VAD, STT, TTS) as internal AgentX components. However, kyutai voice-server already exists as a working external service on port 16000 that handles these concerns efficiently. Instead of duplicating model management, audio processing, and WebSocket protocols, AgentX should focus on what it does best: fast, efficient async text stream handling between frontend and external voice services, conversational state management, and context-aware interactions.

**Problem**: c004 requires implementing VAD, STT, TTS services internally, duplicating kyutai's capabilities and missing optimization opportunities.

**Opportunity**: Treat kyutai voice-server as external dependency, focusing AgentX on:
- Fast async text stream handling (frontend ↔ kyutai server)
- Conversational history and context management
- Error correction and reconnection logic
- Integration with C003 agent pipeline for intelligent responses

---

## What Changes

- **Create voice client infrastructure** for external kyutai service integration
  - Backend: `VoiceGatewayService` to bridge frontend ↔ kyutai server
  - Frontend: `VoiceClient` for WebSocket connection and message handling
  - Text stream handlers for real-time transcription and response streaming

- **Add conversational state management**
  - Conversation history tracking (messages, timestamps, state)
  - Context window management for multi-turn conversations
  - Session persistence across WebSocket reconnections

- **Implement error handling and reconnection**
  - Automatic reconnection with exponential backoff
  - Graceful degradation on kyutai server unavailability
  - Error message translation (kyutai → AgentX protocol)

- **Update C002 data contracts**
  - Add Pydantic models for kyutai protocol messages (Config, Audio, Text, Error, Eos, Heartbeat)
  - Add models for conversational state (ConversationSession, Message, Context)
  - Add Zod schemas for frontend TypeScript parity

- **Update C001 folder structure**
  - Backend: `infrastructure/external/voice_gateway_service.py`
  - Frontend: `lib/voice/client.ts`, `lib/voice/types.ts`
  - Protocol: `infrastructure/external/voice_protocol.py`

- **Deprecate internal voice service implementation** (from c004)
  - **BREAKING**: Remove `VADService`, `STTService`, `TTSService` internal implementations
  - **BREAKING**: Remove direct model loading (Silero VAD, Kyutai STT, Pocket TTS)
  - Migrate to external kyutai service via VoiceGatewayService

---

## Capabilities

### New Capabilities

- **voice-client**: Client infrastructure for connecting to external kyutai voice-server
  - WebSocket connection management (connection, disconnection, reconnection)
  - Message protocol handling (Config, Audio, Text, Error, Eos, Heartbeat)
  - Text stream handling (real-time transcription, response streaming)
  - State synchronization (session state, conversation state)

- **voice-gateway**: Backend service bridging frontend and kyutai server
  - Route messages between frontend and kyutai server
  - Handle conversational state (history, context)
  - Error translation and reconnection logic
  - Integration with C003 agent pipeline

- **conversational-state**: Manage conversation history and context
  - Track messages (user transcripts, agent responses)
  - Maintain context window for multi-turn conversations
  - Session persistence and recovery
  - Context injection into C003 agent queries

- **voice-stream-handling**: Fast async text stream processing
  - Stream transcription chunks to frontend in real-time
  - Stream agent response chunks to TTS in real-time
  - Handle interruption signals from frontend
  - Buffer and debounce audio chunks for efficiency

### Modified Capabilities

- **stt-service**: **BREAKING** - Change from internal implementation to external kyutai client
  - Remove internal Kyutai STT 2.6B model loading
  - Use kyutai server WebSocket endpoint (`ws://localhost:16000/api/v1/ws/stt`)
  - Update protocol to match kyutai message format (Config → Audio chunks → Text responses → Eos)

- **tts-service**: **BREAKING** - Change from internal implementation to external kyutai client
  - Remove internal Pocket TTS model loading
  - Use kyutai server WebSocket endpoint (`ws://localhost:16000/api/v1/ws/tts`)
  - Update protocol to match kyutai message format (Config → Text → Audio chunks → Eos)

- **vad-service**: **BREAKING** - Change from internal implementation to external kyutai client
  - Remove internal Silero VAD model loading
  - Use kyutai server's built-in VAD filtering
  - Remove VAD probability thresholds (handled by kyutai)

- **voice-pipeline**: **BREAKING** - Change orchestration from internal services to external gateway
  - Remove direct VAD/STT/TTS service calls
  - Use VoiceGatewayService for all voice operations
  - Add conversational state management
  - Add error handling and reconnection

- **websocket-protocol**: Add kyutai protocol message types
  - Add `ConfigMessage`, `AudioMessage`, `TextMessage`, `EosMessage`, `ErrorMessage`, `HeartbeatMessage`
  - Add conversational state messages (`ConversationHistoryMessage`, `ContextMessage`)

- **pydantic-zod-sync**: Add voice streaming data contracts
  - Add Pydantic models for kyutai protocol messages
  - Add Zod schemas for frontend TypeScript parity
  - Add conversational state models (ConversationSession, Message, Context)

---

## Impact

### Affected Code

**Backend**:
- Remove: `infrastructure/external/vad_service.py`, `stt_service.py`, `tts_service.py`
- Add: `infrastructure/external/voice_gateway_service.py`
- Add: `infrastructure/external/voice_protocol.py` (kyutai protocol models)
- Modify: `application/use_cases/voice_pipeline_use_case.py` (use VoiceGatewayService)
- Modify: `presentation/api/v1/voice_routes.py` (update WebSocket handling)

**Frontend**:
- Add: `lib/voice/client.ts` (VoiceClient for WebSocket)
- Add: `lib/voice/types.ts` (TypeScript types for voice protocol)
- Add: `lib/voice/conversation.ts` (conversational state management)
- Modify: `app/voice/page.tsx` (use VoiceClient)

**Data Contracts (C002)**:
- Add: `application/dtos/voice_gateway_dtos.py` (kyutai protocol DTOs)
- Add: `application/dtos/conversation_dtos.py` (conversational state DTOs)
- Add: `frontend/types/voice-protocol.ts` (Zod schemas)

**Folder Structure (C001)**:
- Update backend folder structure to include `voice_gateway_service.py`
- Update frontend folder structure to include `lib/voice/`

### Dependencies

**New External Dependencies**:
- **kyutai voice-server**: `ws://localhost:16000` (STT/TTS/VAD service)
  - Must be running for voice features to work
  - Graceful degradation if unavailable

**Removed Internal Dependencies**:
- `torch` (for VAD, STT, TTS model loading)
- `transformers` (for Kyutai STT 2.6B)
- `silero-vad` (for Silero VAD)
- `silero-tts` (for Pocket TTS)

**Retained Dependencies**:
- `fastapi` (WebSocket endpoints)
- `websockets` (client WebSocket connections)
- `pydantic` (data contracts)
- `langgraph` (C003 agent pipeline integration)

### API Changes

**BREAKING**: WebSocket message format changes to match kyutai protocol

**Old Format** (c004 internal):
```json
{"type": "AUDIO_CHUNK", "data": {"audio": "base64...", "sample_rate": 24000}}
```

**New Format** (kyutai protocol):
```json
{"type": "Audio", "data": "base64...", "session_id": "uuid", "timestamp": 1234567890.123}
```

**New REST Endpoints**:
- `GET /api/v1/voice/kyutai/status` - Check kyutai server availability
- `POST /api/v1/voice/conversation/history` - Retrieve conversation history
- `POST /api/v1/voice/conversation/context` - Update conversation context

**Modified WebSocket Endpoints**:
- `/ws/voice` - Updated to use VoiceGatewayService and kyutai protocol

### Migration Path

1. **Phase 1**: Implement VoiceGatewayService and VoiceClient alongside existing services
2. **Phase 2**: Update voice routes to support both protocols (feature flag)
3. **Phase 3**: Deprecate internal VAD/STT/TTS services
4. **Phase 4**: Remove deprecated code after validation

---

**Next Artifact**: design.md
