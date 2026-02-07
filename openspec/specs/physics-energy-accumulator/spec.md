# Spec: Physics Energy Accumulator

Converts continuous audio input into accumulated energy state for driving cell expansion physics.

## Purpose

Transform instantaneous audio levels (0-1) into smooth energy values (0-1) using accumulation and decay, preventing jittery behavior and providing natural momentum for cell movement.

---

## How it LOOKS (Visual)

### Requirement: Energy state visualization

The system SHALL provide optional visual feedback of current energy state for debugging and demo purposes.

#### Scenario: Energy bar indicator

- **WHEN** demo page shows energy state
- **THEN** system displays horizontal progress bar labeled "Energy"
- **AND** bar fills from 0% to 100% based on energy value
- **AND** bar color transitions from purple (low) to pink (high)

#### Scenario: Numeric energy display

- **WHEN** demo page shows detailed state
- **THEN** system displays energy value as decimal: "Energy: 0.73"
- **AND** value updates at 60 FPS during animation

#### Scenario: No visual in production use

- **WHEN** component is used without debug mode
- **THEN** energy state is internal only (no visible indicators)
- **AND** visual feedback comes only from cell expansion

---

## How it WORKS (Behavioral)

### Requirement: Energy accumulation from audio input

The system SHALL accumulate energy from continuous audio input using configurable gain and decay rates.

#### Scenario: Silent audio produces zero energy

- **WHEN** audio level is 0.0 for multiple frames
- **THEN** system decays energy toward 0.0 at decay rate per frame
- **AND** energy eventually reaches near-zero (< 0.01)

#### Scenario: Continuous loud audio produces high energy

- **WHEN** audio level is sustained at 0.8+ for multiple frames
- **THEN** system accumulates energy toward maximum (1.0)
- **AND** energy reaches 0.8+ within ~2 seconds of sustained input

#### Scenario: Brief audio spike produces temporary energy

- **WHEN** audio level spikes to 1.0 for one frame then returns to 0.0
- **THEN** energy increases briefly then decays smoothly
- **AND** energy returns to baseline within ~1 second

---

### Requirement: Configurable energy gain and decay rates

The system SHALL allow configuration of energy accumulation rate (how fast audio adds energy) and decay rate (how fast energy fades when silent).

#### Scenario: Default gain/decay rates

- **WHEN** system initializes with default configuration
- **THEN** energy gain rate is 0.08 per audio unit
- **AND** energy decay rate is 0.96 per frame (multiplicative)

#### Scenario: Custom gain rate for faster response

- **WHEN** system configures gain rate to 0.15
- **THEN** energy accumulates twice as fast from audio input
- **AND** cells reach maximum expansion more quickly

#### Scenario: Custom decay rate for slower fade

- **WHEN** system configures decay rate to 0.98
- **THEN** energy persists longer after silence
- **AND** cells maintain expanded state for extended duration

---

### Requirement: Energy clamping to valid range

The system SHALL clamp accumulated energy to valid range [0.0, 1.0] to prevent invalid states.

#### Scenario: Energy clamps at maximum

- **WHEN** accumulation would push energy above 1.0
- **THEN** system caps energy at exactly 1.0
- **AND** cells use maximum expansion distance

#### Scenario: Energy clamps at minimum

- **WHEN** decay would reduce energy below 0.0
- **THEN** system floors energy at exactly 0.0
- **AND** cells return to merged/baseline state

---

### Requirement: Frame-based energy updates

The system SHALL update energy state once per animation frame using requestAnimationFrame for smooth 60 FPS updates.

#### Scenario: 60 FPS energy updates

- **WHEN** system is running and audio is active
- **THEN** energy updates approximately 60 times per second
- **AND** each update applies accumulation and decay

#### Scenario: Paused updates when tab inactive

- **WHEN** browser tab is inactive (throttled requestAnimationFrame)
- **THEN** energy updates pause or slow down
- **AND** energy state preserves last known value

---

## How it INTERACTS (Integration)

### Requirement: Energy state API

The system SHALL expose current energy value via getter function for consumption by orbit physics and rendering systems.

#### Scenario: Get current energy

- **WHEN** orbit system requests current energy state
- **THEN** system returns number in range [0.0, 1.0]
- **AND** value reflects most recent frame calculation

#### Scenario: Energy updates trigger subscribers

- **WHEN** energy value changes significantly (> 0.01 delta)
- **THEN** system notifies subscribed components
- **AND** components receive new energy value for rendering

---

### Requirement: Audio level input API

The system SHALL accept audio level input via function call from Web Audio API analyzer.

#### Scenario: Receive audio level per frame

- **WHEN** animation loop calls with new audio level
- **THEN** system accepts number in range [0.0, 1.0]
- **AND** system incorporates into energy accumulation

#### Scenario: Handle out-of-range audio

- **WHEN** audio level input exceeds [0.0, 1.0] range
- **THEN** system clamps input to valid range
- **AND** logs warning for invalid values
