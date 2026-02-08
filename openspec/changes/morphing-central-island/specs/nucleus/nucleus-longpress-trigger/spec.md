# Spec: Nucleus Longpress Trigger

Longpress detection (1.5s duration) on central nucleus that triggers mode island spawning.

## Purpose

Define the precise timing, visual feedback, and haptic behavior of the longpress gesture that transforms the nucleus from idle to mode selection state.

---

## How it LOOKS (Visual)

### Requirement: Accelerating pulse animation

The system SHALL display accelerating pulse animation during longpress to indicate progress toward trigger.

#### Scenario: Longpress pulse acceleration

- **WHEN** user begins longpress (mouse down or touch start)
- **THEN** nucleus pulse animation accelerates from 3000ms duration to 500ms duration over 1.5 seconds
- **AND** pulse scale increases from 1.0 → 1.05 to 1.0 → 1.15 (larger scale range)
- **AND** acceleration is smooth (linear easing on duration change)
- **AND** NO progress ring is shown (that's for backend processing only)

#### Scenario: Longpress visual intensity

- **WHEN** longpress progresses from 0ms to 1500ms
- **THEN** nucleus glow intensity increases (box-shadow or drop-shadow)
- **AND** at 1000ms, nucleus has subtle outer glow (`--color-enzyme` cyan #00D9FF)
- **AND** at 1500ms (trigger point), nucleus has medium glow (8px blur, 50% opacity)

---

## How it WORKS (Behavioral)

### Requirement: 1.5 second longpress detection

The system SHALL detect continuous press on nucleus for 1500ms before triggering mode spawn.

#### Scenario: Longpress timing

- **WHEN** user presses nucleus (mouse down or touch start)
- **THEN** system starts 1500ms timer
- **AND** at 1000ms, system triggers haptic feedback (see separate spec)
- **AND** at 1500ms, system triggers mode island spawning
- **AND** timer resets if user releases before 1500ms

#### Scenario: Longpress cancel conditions

- **WHEN** user moves cursor/finger more than 50px away from nucleus center during longpress
- **THEN** longpress is cancelled
- **AND** timer resets
- **AND** nucleus returns to idle state
- **AND** mode islands do NOT spawn

#### Scenario: Early release handling

- **WHEN** user releases press before 1500ms elapsed
- **THEN** longpress is cancelled
- **AND** nucleus returns to idle state immediately
- **AND** no partial feedback is shown (no progress indicator)

### Requirement: Trigger mode island spawning

The system SHALL spawn 4 mode islands in cardinal directions when longpress completes.

#### Scenario: Mode spawn sequence

- **WHEN** longpress reaches 1500ms
- **THEN** 4 mode islands begin spawning from nucleus center
- **AND** spawning is "graceful spill apart" (not explosive burst)
- **AND** islands animate to final cardinal positions (see separate spec)
- **AND** spawning animation uses spring physics (stiffness 200, damping 25)

#### Scenario: Post-trigger nucleus state

- **WHEN** mode islands have spawned
- **THEN** nucleus becomes the "anchor" for mode selection
- **AND** nucleus pulse animation slows back to idle rhythm
- **AND** nucleus maintains centered position
- **AND** clicking any island triggers sequential collapse (see separate spec)

---

## How it's LAYOUT (Positioning)

### Requirement: Nucleus remains centered during longpress

The system SHALL keep nucleus in fixed center position throughout longpress animation.

#### Scenario: No position shift during longpress

- **WHEN** longpress is in progress
- **THEN** nucleus position does NOT change
- **AND** only scale and glow properties animate
- **AND** nucleus center point remains fixed at viewport coordinates

#### Scenario: Longpress interaction area

- **WHEN** user interacts with nucleus for longpress
- **THEN** interaction area is 120px diameter circle (2× nucleus diameter)
- **AND** this accommodates finger touch targets on mobile
- **AND** visual nucleus remains 60px (desktop) or 48px (mobile)
