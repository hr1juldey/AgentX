# Delta Spec: c009-ui-polish

**File**: `specs/voice-interrupt/spec.md`

**Generated**: 2026-01-29
**Change**: c009-ui-polish
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Interrupt Button for Voice Interactions

The interrupt button widget MUST be used for voice interruption during TTS playback.

**Migration Path**: Emit interrupt button via push_ui_message() when TTS starts.

#### Scenario: Interrupt button displayed during TTS

- **WHEN** agent response is sent to kyutai TTS
- **THEN** VoiceGatewayService emits interruptButton UI message via push_ui_message()
- **AND** interruptButton message includes label="Stop"
- **AND** interruptButton message includes action="interrupt_voice"
- **AND** interruptButton message includes variant="destructive" (red outline)
- **AND** ActionComponent renders as button in UI
- **WHEN** user clicks interrupt button
- **THEN** VoiceClient sends Interrupt message to AgentX
- **AND** VoiceGatewayService stops TTS streaming
- **AND** TTS audio playback stops within 200ms

---

**Related Changes**:
- c010-voice-client - Voice interrupt handling via VoiceGatewayService
