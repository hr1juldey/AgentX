# Spec: Longpress Haptic Feedback

Haptic (vibration) feedback at 1000ms during longpress to indicate progress toward mode spawning.

## Purpose

Define the precise timing, duration, and intensity of haptic feedback that provides tactile confirmation during longpress gesture on mobile devices.

---

## How it LOOKS (Visual)

### Requirement: Visual fallback when haptic unavailable

The system SHALL provide visual feedback when haptic feedback is not supported.

#### Scenario: Visual pulse at haptic timing

- **WHEN** haptic feedback triggers at 1000ms
- **THEN** nucleus performs an additional "pulse-jump" animation
- **AND** pulse-jump is scale 1.0 → 1.2 → 1.0 over 200ms
- **AND** this provides visual confirmation equivalent to haptic feedback

#### Scenario: Visual feedback for all devices

- **WHEN** haptic feedback is not supported (desktop, older devices)
- **THEN** pulse-jump animation still occurs at 1000ms
- **AND** user receives visual confirmation regardless of device capability

---

## How it WORKS (Behavioral)

### Requirement: Vibration at 1000ms mark

The system SHALL trigger haptic feedback exactly 1000ms after longpress begins.

#### Scenario: Standard vibration pattern

- **WHEN** longpress timer reaches 1000ms
- **THEN** device vibrates for 200ms duration
- **AND** vibration uses standard intensity (not weak, not strong)
- **AND** vibration pattern is single pulse (not multiple pulses)

#### Scenario: Vibration API call

- **WHEN** haptic feedback triggers
- **THEN** system calls `navigator.vibrate(200)`
- **AND** system wraps call in try-catch (API may be unsupported)
- **AND** system gracefully handles API errors (no crash, silent fallback)

### Requirement: Haptic feedback conditions

The system SHALL only trigger haptic feedback under specific conditions.

#### Scenario: Vibration only during active longpress

- **WHEN** longpress is cancelled before 1000ms
- **THEN** haptic feedback does NOT trigger
- **AND** no vibration occurs

#### Scenario: Vibration once per longpress

- **WHEN** longpress progresses past 1000ms toward 1500ms
- **THEN** haptic feedback triggers only once at 1000ms
- **AND** no additional vibration occurs at 1500ms (mode spawn)

#### Scenario: Vibration on repeat longpress

- **WHEN** user performs multiple longpresses in sequence
- **THEN** each longpress triggers haptic feedback at 1000ms independently
- **AND** previous longpress completion does not affect new longpress

### Requirement: Permission and capability handling

The system SHALL handle device capabilities and permissions gracefully.

#### Scenario: Haptic unsupported fallback

- **WHEN** `navigator.vibrate` is undefined or returns false
- **THEN** system relies on visual feedback only (pulse-jump animation)
- **AND** no error is logged to console
- **AND** user experience is not degraded

#### Scenario: Low-power mode handling

- **WHEN** device is in low-power or battery-saver mode
- **THEN** system attempts haptic feedback (device may suppress)
- **AND** visual feedback always occurs regardless of haptic suppression

---

## How it's LAYOUT (Positioning)

### Requirement: Haptic feedback is device-level

The system SHALL trigger haptic feedback that is independent of on-screen positioning.

#### Scenario: Device vibration vs on-screen feedback

- **WHEN** haptic feedback triggers
- **THEN** vibration affects entire device (not specific to nucleus position)
- **AND** visual feedback (pulse-jump) occurs at nucleus position
- **AND** both feedback types synchronize at 1000ms timestamp

#### Scenario: Multi-device handling

- **WHEN** user interacts across multiple devices (e.g., tablet + connected phone)
- **THEN** haptic feedback triggers on active touch device only
- **AND** visual feedback occurs on display device
