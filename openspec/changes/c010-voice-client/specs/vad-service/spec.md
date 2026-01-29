# Delta Spec: vad-service

**File**: `specs/vad-service/spec.md`

**Generated**: 2026-01-29
**Change**: c010-voice-client

---

## REMOVED Requirements

### Requirement: Internal Silero VAD Model Loading

**Reason**: Replaced by external kyutai voice-server integration. AgentX no longer manages VAD model loading internally. Kyutai server (port 16000) handles all VAD processing internally before STT.

**Migration**:
- Remove `infrastructure/external/vad_service.py`
- VAD filtering now handled by kyutai server (built-in Silero VAD)
- Update `voice_pipeline_use_case.py` to remove VAD pre-processing
- No code changes required for frontend (same WebSocket protocol)

### Requirement: VADService Internal Methods

**Reason**: Internal VADService class removed. All VAD operations now handled by external kyutai server.

**Migration**:
- Remove `VADService.detect_speech()` method calls
- Remove `VADService.adetect_speech()` method calls
- Remove VAD pre-processing from voice pipeline
- Kyutai server filters silence before STT transcription

### Requirement: VAD Speech Probability Threshold

**Reason**: Kyutai server handles VAD threshold tuning internally. AgentX no longer needs to configure or tune speech probability thresholds.

**Migration**:
- Remove `_threshold` configuration parameter
- Remove `DEFAULT_THRESHOLD` constant
- Kyutai server uses its own VAD threshold (configured in kyutai config)

---

## MODIFIED Requirements

### Requirement: VAD Service Architecture

The system MUST use external kyutai voice-server for VAD processing instead of internal model loading.

**Migration Path**:
1. **Phase 1**: Implement `VoiceGatewayService` alongside `VADService` (feature flag)
2. **Phase 2**: Switch default to `VoiceGatewayService` (deprecate `VADService`)
3. **Phase 3**: Remove `VADService` and related code

#### Scenario: VAD filtering via external kyutai server

- **WHEN** frontend sends Audio message to AgentX
- **THEN** `VoiceGatewayService` routes audio to kyutai STT WebSocket endpoint
- **AND** kyutai server applies Silero VAD filtering internally
- **AND** kyutai server only transcribes speech (silence skipped)
- **AND** `VoiceGatewayService` receives Text message only for speech segments

---

**Related Changes**:
- `voice-gateway` spec - New `VoiceGatewayService` for external kyutai integration
- `stt-service` delta spec - STT via external kyutai server

---
