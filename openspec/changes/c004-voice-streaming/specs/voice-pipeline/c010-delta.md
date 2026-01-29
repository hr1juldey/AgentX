# Delta Spec: c004-voice-streaming

**File**: `specs/voice-pipeline/spec.md`

**Generated**: 2026-01-29
**Change**: c004-voice-streaming
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Voice Pipeline Architecture (BREAKING CHANGE)

The voice pipeline MUST use external kyutai voice-server for VAD, STT, and TTS processing instead of internal services.

**Migration Path**:
1. **Phase 1**: Implement VoiceGatewayService alongside internal services (feature flag)
2. **Phase 2**: Switch default to VoiceGatewayService (deprecate internal services)
3. **Phase 3**: Remove internal VAD/STT/TTS services

#### Scenario: Voice request via external kyutai server (NEW)

- **WHEN** frontend sends Audio message to AgentX WebSocket
- **THEN** VoiceGatewayService routes audio to kyutai STT WebSocket endpoint
- **AND** kyutai server applies VAD filtering and transcribes speech to text
- **AND** VoiceGatewayService receives transcript from kyutai
- **AND** ConversationStateManager tracks user message
- **AND** ExecuteAgentQueryUseCase processes transcript with conversation context
- **AND** VoiceGatewayService sends agent response to kyutai TTS WebSocket endpoint
- **AND** kyutai TTS synthesizes text to audio
- **AND** VoiceGatewayService streams audio chunks to frontend
- **AND** ConversationStateManager tracks assistant response

#### Scenario: Internal service deprecation (BREAKING)

- **WHEN** c010-voice-client is implemented
- **THEN** VADService is marked as deprecated
- **AND** STTService is marked as deprecated
- **AND** TTSService is marked as deprecated
- **AND** VoicePipelineUseCase uses VoiceGatewayService instead
- **AND** Feature flag USE_KYUTAI_EXTERNAL controls behavior (Phase 1-2)
- **AND** Internal services removed in Phase 3

---

**Related Changes**:
- c010-voice-client - External kyutai voice-server integration (replaces internal services)
