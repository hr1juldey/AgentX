# Spec: Cell Dismiss Distance Threshold

Distance threshold and timing for cell dismiss gesture when dragged toward nucleus.

## Purpose

Define the precise distance calculation, timing, and trigger point for the cell dismiss gesture.

---

## How it LOOKS (Visual)

### Requirement: Nucleus pulses when ready to receive

The system SHALL display nucleus pulse animation when cell enters dismiss threshold.

#### Scenario: Approaching dismiss zone (200px)

- **WHEN** cell is dragged within 200px of nucleus center
- **THEN** nucleus pulse duration decreases from 1000ms → 500ms (faster rhythm)
- **AND** nucleus glow appears (`--color-enzyme` cyan with 8px blur)

#### Scenario: Within dismiss zone (150px)

- **WHEN** cell enters 150px threshold
- **THEN** nucleus pulse accelerates to 300ms duration (very fast)
- **AND** nucleus glow intensifies to 12px blur, 70% opacity
- **AND** metaball merge activates between cell and nucleus

---

## How it WORKS (Behavioral)

### Requirement: 150px threshold triggers auto-dismiss

The system SHALL automatically dismiss cell when distance < 150px.

#### Scenario: Threshold crossing

- **WHEN** cell distance to nucleus center drops below 150px
- **THEN** dismiss sequence triggers automatically
- **AND** cell animates toward nucleus center (user can release)
- **AND** cell shrink and nucleus absorb animations begin

#### Scenario: User can release early

- **WHEN** cell crosses 150px threshold
- **THEN** user can release mouse/touch
- **AND** dismiss completes automatically (no need to hold drag)
- **AND** this provides "drop into nucleus" interaction

#### Scenario: Moving away cancels dismiss

- **WHEN** cell is dragged away (distance increases beyond 150px)
- **THEN** dismiss is cancelled
- **AND** cell stops moving toward nucleus
- **AND** nucleus returns to normal pulse rhythm

---

## How it's LAYOUT (Positioning)

### Requirement: Distance is center-to-center

The system SHALL calculate distance from cell center to nucleus center.

#### Scenario: Distance calculation

- **WHEN** calculating dismiss distance
- **THEN** distance = Euclidean distance between cell center and nucleus center
- **AND** threshold is 150px (desktop) or 120px (mobile)
- **AND** recalculate every frame during drag

#### Scenario: Visual feedback zone

- **WHEN** cell is in 150-200px range (approaching)
- **THEN** nucleus shows "ready" feedback (faster pulse, glow)
- **AND** this is visual feedback zone (dismiss not yet triggered)
