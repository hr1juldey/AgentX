# Spec: Voice Nucleus Mic Toggle

Microphone toggle icon and state management for voice mode nucleus.

## Purpose

Define the visual appearance, interaction behavior, and state transitions for the microphone toggle that appears in the center of voice mode nucleus.

---

## How it LOOKS (Visual)

### Requirement: Mic icon in nucleus center

The system SHALL display microphone icon in center of nucleus when voice mode is active.

#### Scenario: Mic icon appearance

- **WHEN** voice mode becomes active (sequential collapse complete)
- **THEN** nucleus maintains circular shape (does NOT morph to bar)
- **AND** nucleus color is `--color-endoplasmic` (#C792EA purple)
- **AND** nucleus center displays Mic icon from Lucide React
- **AND** icon color is `--color-nucleus` (#FFFFFF white)
- **AND** icon size is 28px (slightly larger than mode island icons)

#### Scenario: Mic off state

- **WHEN** voice mode is active but microphone is off
- **THEN** Mic icon displays with slash through it (MicOff icon variant)
- **AND** icon opacity is 0.7 (dimmed, indicating inactive)
- **AND** nucleus pulse animation is slow (3000ms duration)

#### Scenario: Mic on state

- **WHEN** user has toggled microphone on
- **THEN** Mic icon displays without slash (Mic icon variant)
- **AND** icon opacity is 1.0 (full brightness)
- **AND** icon has subtle glow effect (box-shadow, `--color-golgi` gold)
- **AND** nucleus pulse animation is faster (1000ms duration, indicating active listening)

---

## How it WORKS (Behavioral)

### Requirement: Toggle mic on click

The system SHALL toggle microphone state when user clicks nucleus center.

#### Scenario: Click to turn mic on

- **WHEN** user clicks voice mode nucleus (mic icon)
- **AND** microphone is currently off
- **THEN** microphone turns on
- **AND** system requests microphone permission if not granted
- **AND** on success, mic icon changes to Mic (no slash)
- **AND** icon glow appears indicating active listening

#### Scenario: Click to turn mic off

- **WHEN** user clicks voice mode nucleus (mic icon)
- **AND** microphone is currently on
- **THEN** microphone turns off
- **AND** audio capture stops
- **AND** mic icon changes to MicOff (with slash)
- **AND** icon glow disappears

#### Scenario: Permission denial handling

- **WHEN** user denies microphone permission
- **THEN** system shows error message (toast notification)
- **AND** mic icon remains in MicOff state
- **AND** nucleus does NOT enter active listening state

### Requirement: Visual feedback during listening

The system SHALL provide visual feedback when audio is being detected.

#### Scenario: Audio level visualization

- **WHEN** microphone is on and audio is detected
- **THEN** nucleus edge pulses in sync with audio level
- **AND** pulse intensity scales with audio volume
- **AND** this provides "I hear you" feedback to user

#### Scenario: No audio feedback

- **WHEN** microphone is on but no audio detected
- **THEN** nucleus maintains steady pulse (1000ms duration)
- **AND** no additional visual feedback occurs
- **AND** this indicates "waiting for speech" state

---

## How it's LAYOUT (Positioning)

### Requirement: Icon centered in nucleus

The system SHALL position mic icon perfectly centered within nucleus circle.

#### Scenario: Icon centering

- **WHEN** voice mode nucleus is rendered
- **THEN** mic icon is at `top: 50%, left: 50%, transform: translate(-50%, -50%)`
- **AND** icon maintains 28px size regardless of nucleus size
- **AND** icon has 16px clearance from nucleus edge (60px nucleus)

#### Scenario: Nucleus size

- **WHEN** voice mode is active
- **THEN** nucleus is 60px diameter circle (desktop) or 48px (mobile)
- **AND** nucleus position is viewport center (same as idle nucleus)
- **AND** nucleus does NOT shift position during voice mode activation

#### Scenario: Glow positioning

- **WHEN** mic is on and icon glow is active
- **THEN** glow is centered on icon
- **AND** glow does NOT extend beyond nucleus edge
- **AND** glow is `--color-golgi` (#FFD700 gold) with 8px blur
