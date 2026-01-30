# Spec: voice-nucleus

**File**: `specs/voice-nucleus/spec.md`

## 1.1 Purpose

Define the central voice interface component that serves as the visual and interaction hub for all voice operations, featuring platform-aware sizing (160px desktop, 72px mobile), positioning (center desktop, bottom-center mobile), pulse animation when active, drift animation when idle, and full accessibility support.

## 1.2 Scope

**In Scope**:
- Voice nucleus component (160px desktop, 72px mobile)
- Platform-aware positioning (center desktop, bottom-center mobile)
- Pulse animation when active (voice recording/playback)
- Drift animation when idle (breathing motion)
- Mitosis animation for widget spawning (start as tiny circles, morph into rounded rectangles)
- Touch target compliance (minimum 44px)
- Accessibility (keyboard navigation, screen reader, reduced motion)
- Z-index layering (layer.voice: 40)

**Out of Scope**:
- WebSocket connection (C004 voice-streaming)
- Audio capture/playback (C004 voice-streaming)
- Transcript rendering (handled by transcript widget)
- Widget layout system (anchors, mobile stack)
- Widget spawning logic (handled by LangGraph)

## 1.3 Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-VN-001 | Nucleus size MUST be platform-aware (160px desktop, 72px mobile) | Must |
| FR-VN-002 | Position MUST be platform-aware (center desktop, bottom-center mobile) | Must |
| FR-VN-003 | Active state MUST show pulse animation (scale: [1, 1.08, 1], boxShadow: [glow, pulse, glow]) | Must |
| FR-VN-004 | Idle state MUST show drift animation (y: [0, -8, 0], x: [0, 4, 0]) | Must |
| FR-VN-005 | Touch target MUST be minimum 44px (72px satisfies this) | Must |
| FR-VN-006 | Keyboard accessible (Space key toggles voice state) | Must |
| FR-VN-007 | Screen reader label MUST be accurate ("Start speaking" / "Stop speaking") | Must |
| FR-VN-008 | Reduced motion preference MUST disable animations | Must |
| FR-VN-009 | Voice layer MUST be at z-index 40 (above widgets, below modals) | Must |
| FR-VN-010 | Nucleus MUST use `Nucleus` primitive component | Must |
| FR-VN-011 | Voice nucleus widget MUST integrate with server-driven UI for voice state | Must |

### Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-VN-001 | Pulse animation MUST complete in 1.4s (breathing rhythm) | Should |
| NFR-VN-002 | Drift animation MUST complete in 2.4s (relaxed floating) | Should |
| NFR-VN-003 | Component MUST be SSR-safe (no `window` access during render) | Should |
| NFR-VN-004 | Focus ring MUST be visible (`focus-visible:ring-2 ring-enzyme`) | Should |

---

## 1.3.1 Voice Nucleus Widget for Voice State

The voice nucleus widget MUST be used for voice state visual feedback during voice interactions.

**Migration Path**: Register voice nucleus widget in agent/ui.tsx for server-driven UI emission.

### Scenario: Voice nucleus widget displays voice state

- **WHEN** voice interaction starts
- **THEN** VoiceGatewayService emits voiceStatus UI message via push_ui_message()
- **AND** voiceStatus message includes state (listening/processing/speaking)
- **AND** voiceStatus message includes icon (mic/brain/speaker)
- **AND** voiceStatus message includes pulse flag for animation
- **AND** VoiceNucleusWidget renders with platform-aware sizing (160px desktop, 72px mobile)
- **AND** VoiceNucleusWidget uses design tokens from design-tokens.ts
- **AND** Metaball effects use platform-aware blur (16px desktop, 12px mobile)

### Scenario: Voice nucleus widget integration

- **WHEN** voice state changes during conversation
- **THEN** VoiceNucleusWidget updates based on voiceStatus message
- **AND** VoiceNucleusWidget uses Shadow DOM for style isolation
- **AND** VoiceNucleusWidget is registered in agent/ui.tsx

**Related Changes**:
- c010-voice-client - Voice state UI emission via VoiceGatewayService

---

## 1.4 Data Model

**Locked from LLD** (agentx_organic_ui_design_system.md:657-703, 1006-1056):

```typescript
// Voice Button Props
interface VoiceButtonProps {
  active: boolean  // True when recording or playing audio
  onToggle: () => void  // Callback to toggle voice state
}

// Nucleus Primitive Props
interface NucleusProps {
  size?: number  // 160 (desktop) or 72 (mobile)
  active?: boolean  // Show pulse animation
  children?: React.ReactNode  // Inner content (e.g., microphone icon)
  className?: string  // Additional CSS classes
  style?: React.CSSProperties  // Additional inline styles
}

// Platform Detection (from capability.isMobile())
const isMobile = window.innerWidth < 1024 || navigator.userAgent.match(/iPhone|iPad|Android/i)
const size = isMobile ? 72 : 160
const positionStyle = isMobile
  ? { position: 'fixed', bottom: 24, left: '50%', transform: 'translateX(-50%)' }
  : { position: 'absolute', bottom: '50%', left: '50%', transform: 'translate(-50%, 50%)' }
```

**Animation Presets** (Locked from design/motion.ts):
```typescript
// Pulse (active state)
const pulse = {
  animate: {
    scale: [1, 1.08, 1],
    boxShadow: [tokens.shadow.glow, tokens.shadow.pulse, tokens.shadow.glow],
  },
  transition: { duration: 1.4, repeat: Infinity, ease: 'easeInOut' },
}

// Drift (idle state)
const drift = {
  animate: { y: [0, -8, 0], x: [0, 4, 0] },
  transition: { duration: 2.4, repeat: Infinity, ease: 'easeInOut' },
}
```

## 1.5 API Contract

**Note**: This spec has no API contracts (frontend-only).

## 1.6 Business Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| BR-VN-001 | Size MUST be 160px on desktop, 72px on mobile | Runtime check (`capability.isMobile()`) |
| BR-VN-002 | Position MUST be center (desktop) or bottom-center (mobile) | Conditional inline styles |
| BR-VN-003 | Active state MUST trigger pulse animation | Framer Motion `animate` prop |
| BR-VN-004 | Idle state MUST trigger drift animation | Framer Motion `animate` prop |
| BR-VN-005 | Space key MUST toggle voice state | `onKeyDown` handler |
| BR-VN-006 | ARIA label MUST reflect current state | `aria-label={active ? "Stop speaking" : "Start speaking"}` |
| BR-VN-007 | ARIA pressed MUST reflect current state | `aria-pressed={active}` |
| BR-VN-008 | Reduced motion MUST disable all animations | Check `capability.prefersReducedMotion()` |

## 1.7 Acceptance Criteria

- [ ] Nucleus renders at 160px on desktop, 72px on mobile
- [ ] Position center (desktop) or bottom-center (mobile, 24px from bottom)
- [ ] Pulse animation when active (scale 1.08, glow → pulse → glow)
- [ ] Drift animation when idle (y: -8→0→8, x: 0→4→0)
- [ ] Space key toggles voice state
- [ ] ARIA label accurate ("Start speaking" / "Stop speaking")
- [ ] ARIA pressed reflects state (true when active)
- [ ] Animations respect `prefers-reduced-motion`
- [ ] Touch target ≥44px (72px satisfies)
- [ ] Focus ring visible on keyboard focus
- [ ] Voice layer at z-index 40
- [ ] Uses `Nucleus` primitive component
- [ ] SSR-safe (no `window` access during render)
- [ ] Pulse duration 1.4s (breathing rhythm)
- [ ] Drift duration 2.4s (relaxed floating)
