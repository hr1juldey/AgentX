# Spec: Voice Cell Separation Trajectory

Trajectory and timing for voice cell separating from nucleus and traveling to final position.

## Purpose

Define the path, timing, and spring physics for cell widget traveling from nucleus edge to final force-layout position.

---

## How it LOOKS (Visual)

### Requirement: Cell separates and travels outward

The system SHALL animate cell separating from nucleus and traveling outward to final position.

#### Scenario: Separation from nucleus

- **WHEN** bud formation completes (bud attached to nucleus edge)
- **THEN** cell separates from nucleus (metaball connection breaks)
- **AND** cell travels outward along trajectory
- **AND** separation is clean (no stretched gooey bridge)

#### Scenario: Travel trajectory

- **WHEN** cell travels from nucleus to final position
- **THEN** trajectory is direct line (not curved path)
- **AND** trajectory is from edge position → force-layout calculated position
- **AND** travel distance is ~200px (30% of screen width, not to viewport edge)
- **AND** cell maintains scale 1 throughout travel

---

## How it WORKS (Behavioral)

### Requirement: Spring-physics travel

The system SHALL use spring physics for organic travel motion.

#### Scenario: Travel spring configuration

- **WHEN** cell begins traveling
- **THEN** spring stiffness is 150 (softer than other animations)
- **AND** spring damping is 20 (bouncy)
- **AND** travel duration is approximately 400ms
- **AND** cell may slightly overshoot target then settle

#### Scenario: Travel phases

- **WHEN** cell travels from nucleus to target
- **THEN** Phase 1 (0-200ms): Accelerate outward from nucleus
- **AND** Phase 2 (200-400ms): Decelerate as approaching target
- **AND** Phase 3 (400-600ms): Arrive and bounce once (settling)

#### Scenario: Multiple cells travel simultaneously

- **WHEN** multiple cells spawn simultaneously
- **THEN** all cells travel simultaneously (not sequentially)
- **AND** each cell has independent spring animation
- **AND** cells do NOT collide during travel (force layout prevents this)

---

## How it's LAYOUT (Positioning)

### Requirement: Target position from force layout

The system SHALL calculate target position using force layout simulation.

#### Scenario: Target calculation

- **WHEN** cell is ready to travel
- **THEN** force layout calculates target position based on all cells
- **AND** target is position in circle around nucleus (see force layout spec)
- **AND** travel distance = distance from edge position → target position
- **AND** typical travel distance is 150-250px

#### Scenario: Trajectory is direct line

- **WHEN** cell travels from start to target
- **THEN** path is straight line (no curves)
- **AND** cell position updates every frame via spring physics
- **AND** final position aligns exactly with force-layout target

#### Scenario: Viewport bounds checking

- **WHEN** target position is calculated
- **THEN** system ensures target is within viewport bounds
- **AND** target has minimum 50px clearance from viewport edges
- **AND** if target would be out of bounds, force layout adjusts radius
