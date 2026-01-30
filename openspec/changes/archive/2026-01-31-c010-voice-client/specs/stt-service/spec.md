# Delta Spec: stt-service

**File**: `specs/stt-service/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## REMOVED Requirements

### Requirement: Internal Kyutai STT 2.6B Model Loading

**Reason**: Replaced by external kyutai voice-server integration. AgentX no longer manages STT model loading internally. Kyutai server (port 16000) handles all STT processing.

**Migration**:
- Remove `infrastructure/external/stt_service.py`
- Use `VoiceGatewayService` to connect to kyutai STT WebSocket endpoint
- Update `voice_pipeline_use_case.py` to use `VoiceGatewayService` instead of `STTService`
- No code changes required for frontend (same WebSocket protocol)

### Requirement: STTService Internal Methods

**Reason**: Internal STTService class removed. All STT operations now handled by external kyutai server.

**Migration**:
- Remove `STTService.transcribe()` method calls
- Remove `STTService.atranscribe()` method calls
- Use `VoiceGatewayService._input_task()` for routing audio to kyutai STT
- Use `VoiceGatewayService._output_task()` for receiving transcripts from kyutai

### Requirement: STT Audio Preprocessing (Resample, Mono)

**Reason**: Kyutai server handles all audio preprocessing. AgentX no longer needs to resample or convert audio.

**Migration**:
- Remove `_resample_audio()` and `_to_mono()` methods
- Send raw audio chunks directly to kyutai server via `VoiceGatewayService`
- Kyutai server handles resampling to 16kHz internally

---

## MODIFIED Requirements

### Requirement: STT Service Architecture

The system MUST use external kyutai voice-server for STT processing instead of internal model loading.

**Migration Path**:
1. **Phase 1**: Implement `VoiceGatewayService` alongside `STTService` (feature flag)
2. **Phase 2**: Switch default to `VoiceGatewayService` (deprecate `STTService`)
3. **Phase 3**: Remove `STTService` and related code

#### Scenario: STT via external kyutai server

- **WHEN** frontend sends Audio message to AgentX WebSocket
- **THEN** `VoiceGatewayService` routes audio to kyutai STT WebSocket endpoint
- **AND** kyutai STT transcribes audio to text
- **AND** `VoiceGatewayService` receives Text message from kyutai
- **AND** `VoiceGatewayService` sends transcript to frontend and agent pipeline

#### Scenario: Fallback to text-only mode

- **WHEN** kyutai STT server is unavailable
- **THEN** `VoiceGatewayService` returns error to frontend
- **AND** frontend shows "Voice unavailable. Using text mode." message
- **AND** user can still interact via text input

---

**Related Changes**:
- `voice-gateway` spec - New `VoiceGatewayService` for external kyutai integration
- `voice-client` spec - Frontend client for WebSocket connections
- `websocket-protocol` delta spec - Kyutai message format support

---
