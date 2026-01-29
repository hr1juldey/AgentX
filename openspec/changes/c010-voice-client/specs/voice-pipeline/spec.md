# Delta Spec: voice-pipeline

**File**: `specs/voice-pipeline/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## REMOVED Requirements

### Requirement: Internal Voice Pipeline Orchestration (VAD → STT → LLM → TTS)

**Reason**: Replaced by external kyutai voice-server integration. VoicePipelineUseCase no longer orchestrates internal VAD, STT, and TTS services directly. Instead, it uses VoiceGatewayService to bridge frontend to kyutai server.

**Migration**:
- Remove direct calls to `VADService`, `STTService`, `TTSService`
- Use `VoiceGatewayService.handle_session()` for all voice operations
- Update `voice_pipeline_use_case.py` to use `VoiceGatewayService`
- Conversational state management now handled by `ConversationStateManager`

### Requirement: Audio Resampling in Pipeline

**Reason**: Kyutai server handles all audio preprocessing. VoicePipelineUseCase no longer needs to resample audio.

**Migration**:
- Remove audio resampling logic from voice pipeline
- Send raw audio chunks directly to `VoiceGatewayService`
- Kyutai server handles resampling to required sample rates

---

## MODIFIED Requirements

### Requirement: Voice Pipeline Architecture

The voice pipeline MUST use external kyutai voice-server for VAD, STT, and TTS processing instead of internal services.

**Migration Path**:
1. **Phase 1**: Implement `VoiceGatewayService` alongside `VoicePipelineUseCase` (feature flag)
2. **Phase 2**: Switch default to `VoiceGatewayService` (deprecate internal services)
3. **Phase 3**: Remove internal service orchestration from `VoicePipelineUseCase`

#### Scenario: Voice request via external kyutai server

- **WHEN** frontend sends Audio message to AgentX WebSocket
- **THEN** `VoiceGatewayService` routes audio to kyutai STT WebSocket endpoint
- **AND** kyutai server applies VAD filtering and transcribes speech to text
- **AND** `VoiceGatewayService` receives transcript from kyutai
- **AND** `ConversationStateManager.add_user_message()` tracks the transcript
- **AND** `ExecuteAgentQueryUseCase.execute()` processes transcript with conversation context
- **AND** `VoiceGatewayService` sends agent response to kyutai TTS WebSocket endpoint
- **AND** kyutai TTS synthesizes text to audio
- **AND** `VoiceGatewayService` streams audio chunks to frontend
- **AND** `ConversationStateManager.add_assistant_message()` tracks the response
- **AND** end-to-end latency <500ms (P95), target <300ms (P50)

#### Scenario: Voice interruption

- **WHEN** user presses interrupt button during TTS playback
- **THEN** frontend sends Interrupt message to AgentX
- **AND** `VoiceGatewayService` sets session.interrupted flag
- **AND** `TextStreamHandler.interrupt_tts()` stops streaming
- **AND** `VoiceGatewayService` closes kyutai TTS WebSocket connection
- **AND** frontend stops audio playback
- **AND** interruption latency <200ms (P95)

#### Scenario: Conversational context injection

- **WHEN** user sends follow-up question (e.g., "And in New York?")
- **THEN** `ConversationStateManager.get_conversation_history()` returns previous messages
- **AND** `ConversationContext` contains topic="weather", entities=["San Francisco"]
- **AND** `ExecuteAgentQueryUseCase.execute()` receives conversation context
- **AND** agent response references previous context (e.g., "The weather in New York is 65°F")
- **AND** `ConversationStateManager.update_context()` updates topic and entities

---

**Related Changes**:
- `voice-gateway` spec - New `VoiceGatewayService` for external kyutai integration
- `conversational-state` spec - Conversation state management
- `voice-stream-handling` spec - Text stream processing
- `stt-service` delta spec - STT via external kyutai server
- `tts-service` delta spec - TTS via external kyutai server
- `vad-service` delta spec - VAD via external kyutai server

---
