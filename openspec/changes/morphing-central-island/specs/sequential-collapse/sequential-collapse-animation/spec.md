# Spec: Sequential Collapse Animation

Animation characteristics (easing, spring physics) for mode islands sliding and merging during sequential collapse.

## Purpose

Define the precise spring configuration, easing curves, and animation behavior for the biological engulfing motion during sequential collapse.

---

## How it LOOKS (Visual)

### Requirement: Smooth slide with spring overshoot

The system SHALL animate island slide with spring physics that creates slight overshoot then settle.

#### Scenario: Slide animation curve

- **WHEN** island slides toward selected island
- **THEN** island moves with spring physics (not cubic-bezier)
- **AND** island may slightly overshoot target position then settle back
- **AND** overshoot is approximately 5-10% of slide distance
- **AND** settle animation completes within 50ms after initial arrival

#### Scenario: Smooth motion without jank

- **WHEN** slide animation is in progress
- **THEN** animation maintains 60 FPS
- **AND** no frame drops or stuttering occurs
- **AND** motion appears fluid and organic

---

## How it WORKS (Behavioral)

### Requirement: Spring configuration for collapse

The system SHALL use specific spring values for collapse animation.

#### Scenario: Spring stiffness and damping

- **WHEN** island slide begins
- **THEN** spring stiffness is 400 (snappy, responsive)
- **AND** spring damping is 20 (low damping = bouncy)
- **AND** this combination creates quick slide with elastic bounce
- **AND** animation duration is approximately 200ms

#### Scenario: Velocity accumulation

- **WHEN** island slides toward target
- **THEN** island accumulates velocity in direction of target
- **AND** velocity carries island slightly past target (overshoot)
- **AND** reverse spring force pulls island back to target
- **AND** damping settles oscillation within 2-3 bounce cycles

#### Scenario: Animation performance optimization

- **WHEN** multiple islands collapse sequentially
- **THEN** only ONE island is animating at any moment
- **AND** this prevents performance degradation
- **AND** GPU-accelerated transforms (translate3d) are used
- **AND** layout reflows are avoided (use transform, not top/left)

---

## How it's LAYOUT (Positioning)

### Requirement: Position interpolation during slide

The system SHALL calculate island position smoothly during slide animation.

#### Scenario: Start and end positions

- **WHEN** island slide begins
- **THEN** start position is island's current cardinal position
- **AND** end position is selected island's position (center)
- **AND** slide distance is 80-120px depending on which islands

#### Scenario: Position update frequency

- **WHEN** slide animation is running
- **THEN** position updates every frame (60 FPS = ~16.7ms intervals)
- **AND** position is calculated via spring physics function
- **AND** no position jumps or teleportation occurs

#### Scenario: Final position alignment

- **WHEN** island completes slide and arrives at target
- **THEN** island position aligns exactly with selected island position
- **AND** pixel-perfect alignment (no subpixel gaps)
- **AND** this enables clean metaball merge
