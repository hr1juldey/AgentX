# Spec: voice-interrupt

**File**: `specs/voice-interrupt/spec.md`

## 1.1 Purpose

Define the voice interrupt mechanism that provides a clear, obvious way for users to interrupt voice responses.

## 1.2 Scope

**In Scope**:
- Interrupt button (desktop: Space, mobile: tap button)
- Visual feedback (interrupt animation)
- Touch target compliance (44px minimum)
- ARIA labels ("Tap to interrupt")

**Out of Scope**:
- WebSocket connection (C004)
- Audio playback (C004)
- Voice nucleus component (C008)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VI-001 | Interrupt button MUST spawn during audio playback | Must |
| FR-VI-002 | Interrupt button MUST use interrupt animation | Must |
| FR-VI-003 | Desktop: Space key MUST interrupt voice playback | Must |
| FR-VI-004 | Mobile: Tap button MUST interrupt voice playback | Must |
| FR-VI-005 | Touch target MUST be ≥44px | Must |
| FR-VI-006 | ARIA label MUST be "Tap to interrupt" or "Press Space to interrupt" | Must |

## 1.4 Acceptance Criteria

- [ ] Interrupt button spawns during audio playback
- [ ] Interrupt animation plays
- [ ] Space key interrupts on desktop
- [ ] Tap button interrupts on mobile
- [ ] Touch target ≥44px
- [ ] ARIA label accurate
- [ ] Audio fades out on interrupt
