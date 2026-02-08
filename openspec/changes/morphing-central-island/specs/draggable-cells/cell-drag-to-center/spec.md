# Spec: Cell Drag to Center

Drag-to-center dismiss gesture where user drags cell toward nucleus to dismiss it.

## Purpose

Define the distance threshold, visual feedback, and trigger behavior for the drag-to-center dismiss gesture.

---

## How it LOOKS (Visual)

### Requirement: Visual feedback when approaching nucleus

The system SHALL provide visual feedback when cell is dragged toward nucleus center.

#### Scenario: Approaching dismiss threshold

- **WHEN** cell is dragged within 200px of nucleus center
- **THEN** nucleus begins pulsing (faster rhythm)
- **AND** nucleus glow appears (`--color-enzyme` cyan)
- **AND** this indicates "ready to receive cell"

#### Scenario: Within dismiss threshold

- **WHEN** cell is dragged within 150px of nucleus center
- **THEN** nucleus pulse accelerates further (500ms duration)
- **AND** nucleus glow intensifies (12px blur, 70% opacity)
- **AND** metaball merge begins between cell and nucleus

#### Scenario: Contact with nucleus

- **WHEN** cell contacts nucleus (distance < nucleus radius + cell radius)
- **THEN** metaball merge is fully active (cells appear fused)
- **AND** cell begins shrinking (scale 1.0 → 0.5)
- **AND** nucleus absorbs cell (see separate spec)

---

## How it WORKS (Behavioral)

### Requirement: 150px dismiss threshold

The system SHALL trigger dismiss gesture when cell is within 150px of nucleus center.

#### Scenario: Dismiss threshold

- **WHEN** cell center distance to nucleus center < 150px
- **THEN** dismiss gesture is triggered
- **AND** cell automatically animates toward nucleus center
- **AND** user can release mouse/touch (dismiss completes automatically)

#### Scenario: User must drag cell (not throw)

- **WHEN** user releases cell before entering 150px threshold
- **THEN** cell stays at released position (does NOT move toward nucleus)
- **AND** dismiss is NOT triggered
- **AND** cell remains draggable for future attempt

#### Scenario: Drag away cancels dismiss

- **WHEN** user drags cell away from nucleus (distance increases beyond 150px)
- **THEN** dismiss is cancelled
- **AND** cell stops moving toward nucleus
- **AND** cell becomes draggable normally again

---

## How it's LAYOUT (Positioning)

### Requirement: Distance calculation to nucleus center

The system SHALL calculate Euclidean distance from cell center to nucleus center.

#### Scenario: Distance formula

- **WHEN** calculating distance for dismiss threshold
- **THEN** distance = `sqrt((cell.x - nucleus.x)^2 + (cell.y - nucleus.y)^2)`
- **AND** compare distance to 150px threshold
- **AND** recalculate distance every frame during drag

#### Scenario: Nucleus center position

- **WHEN** calculating distance
- **THEN** nucleus center is viewport center (fixed position)
- **AND** nucleus center coordinates are: `{ x: viewportWidth / 2, y: viewportHeight / 2 }`
- **AND** on mobile, nucleus may be offset (see nucleus positioning spec)
