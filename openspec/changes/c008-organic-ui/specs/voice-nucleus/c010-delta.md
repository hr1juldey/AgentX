# Delta Spec: c008-organic-ui

**File**: `specs/voice-nucleus/spec.md`

**Generated**: 2026-01-29
**Change**: c008-organic-ui
**Related**: c010-voice-client

---

## MODIFIED Requirements

### Requirement: Voice Nucleus Widget for Voice State

The voice nucleus widget MUST be used for voice state visual feedback during voice interactions.

**Migration Path**: Register voice nucleus widget in agent/ui.tsx for server-driven UI emission.

#### Scenario: Voice nucleus widget displays voice state

- **WHEN** voice interaction starts
- **THEN** VoiceGatewayService emits voiceStatus UI message via push_ui_message()
- **AND** voiceStatus message includes state (listening/processing/speaking)
- **AND** voiceStatus message includes icon (mic/brain/speaker)
- **AND** voiceStatus message includes pulse flag for animation
- **AND** VoiceNucleusWidget renders with platform-aware sizing (160px desktop, 72px mobile)
- **AND** VoiceNucleusWidget uses design tokens from design-tokens.ts
- **AND** Metaball effects use platform-aware blur (16px desktop, 12px mobile)

#### Scenario: Voice nucleus widget integration

- **WHEN** voice state changes during conversation
- **THEN** VoiceNucleusWidget updates based on voiceStatus message
- **AND** VoiceNucleusWidget uses Shadow DOM for style isolation
- **AND** VoiceNucleusWidget is registered in agent/ui.tsx

---

**Related Changes**:
- c010-voice-client - Voice state UI emission via VoiceGatewayService
