# Delta Spec: tts-service

**File**: `specs/tts-service/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## REMOVED Requirements

### Requirement: Internal Pocket TTS Model Loading

**Reason**: Replaced by external kyutai voice-server integration. AgentX no longer manages TTS model loading internally. Kyutai server (port 16000) handles all TTS processing, including memory management.

**Migration**:
- Remove `infrastructure/external/tts_service.py`
- Use `VoiceGatewayService` to connect to kyutai TTS WebSocket endpoint
- Update `voice_pipeline_use_case.py` to use `VoiceGatewayService` instead of `TTSService`
- No code changes required for frontend (same WebSocket protocol)

### Requirement: TTSService Internal Methods

**Reason**: Internal TTSService class removed. All TTS operations now handled by external kyutai server.

**Migration**:
- Remove `TTSService.synthesize()` method calls
- Remove `TTSService.astream_synthesize()` method calls
- Use `VoiceGatewayService._input_task()` for sending text to kyutai TTS
- Use `VoiceGatewayService._output_task()` for receiving audio from kyutai

### Requirement: TTS Memory Management (Model Reload)

**Reason**: Kyutai server handles all memory management internally. AgentX no longer needs to reload TTS model to prevent memory leaks.

**Migration**:
- Remove `_reload_model()` method and `_generation_count` tracking
- Kyutai server handles Pocket TTS memory management
- Observed 32GB+ memory growth issue no longer affects AgentX

### Requirement: TTS Audio Chunking

**Reason**: Kyutai server handles audio chunking and streaming. AgentX no longer needs to split audio into 500ms chunks.

**Migration**:
- Remove `_chunk_audio()` method
- Kyutai server streams audio chunks in its own format
- AgentX passes audio chunks directly to frontend

---

## MODIFIED Requirements

### Requirement: TTS Service Architecture

The system MUST use external kyutai voice-server for TTS processing instead of internal model loading.

**Migration Path**:
1. **Phase 1**: Implement `VoiceGatewayService` alongside `TTSService` (feature flag)
2. **Phase 2**: Switch default to `VoiceGatewayService` (deprecate `TTSService`)
3. **Phase 3**: Remove `TTSService` and related code

#### Scenario: TTS via external kyutai server

- **WHEN** agent pipeline generates text response
- **THEN** `VoiceGatewayService` sends text to kyutai TTS WebSocket endpoint
- **AND** kyutai TTS synthesizes text to audio
- **AND** `VoiceGatewayService` receives Audio messages from kyutai
- **AND** `VoiceGatewayService` streams audio chunks to frontend
- **AND** frontend plays audio via browser Audio API

#### Scenario: TTS interruption

- **WHEN** user presses "Stop" button during TTS playback
- **THEN** frontend sends Interrupt message to AgentX
- **AND** `VoiceGatewayService` sets session.interrupted flag
- **AND** `TextStreamHandler.interrupt_tts()` stops streaming
- **AND** kyutai TTS stops synthesis (connection closes)
- **AND** frontend stops audio playback

---

**Related Changes**:
- `voice-gateway` spec - New `VoiceGatewayService` for external kyutai integration
- `voice-stream-handling` spec - Text stream processing for TTS
- `websocket-protocol` delta spec - Kyutai message format support

---
