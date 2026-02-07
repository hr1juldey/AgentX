# Spec: Physics Orbit Mechanics

Orbital motion system for cells rotating around central nucleus with independent angular velocities.

## Purpose

Manage continuous orbital rotation of multiple cells around a central nucleus, with each cell maintaining independent angular position, speed, and phase offset.

---

## How it LOOKS (Visual)

### Requirement: Visual orbital motion

The system SHALL render cells orbiting around central nucleus in clockwise direction with subtle speed variations.

#### Scenario: 8 cells orbiting smoothly

- **WHEN** system renders with 8 cells at energy 0.5
- **THEN** cells appear distributed evenly around nucleus
- **AND** cells rotate clockwise continuously
- **AND** cells maintain relative separation while orbiting

#### Scenario: Nucleus counter-rotation

- **WHEN** cells orbit clockwise
- **THEN** nucleus rotates slowly counter-clockwise
- **AND** rotation creates dynamic visual interest

#### Scenario: Variable orbital speeds

- **WHEN** multiple cells orbit simultaneously
- **THEN** faster cells occasionally overtake slower cells
- **AND** relative positions shift organically over time

---

## How it WORKS (Behavioral)

### Requirement: Cell orbital position tracking

The system SHALL track each cell's orbital angle in radians [0, 2π] and update continuously per frame.

#### Scenario: Initial cell positions distributed

- **WHEN** system initializes with 8 cells
- **THEN** cells are distributed at equal angles: 0, π/4, π/2, 3π/4, π, 5π/4, 3π/2, 7π/4
- **AND** each cell has unique angle offset

#### Scenario: Continuous orbital rotation

- **WHEN** animation frame updates
- **THEN** each cell angle increases by its orbital speed
- **AND** angles wrap around at 2π (modulo arithmetic)

#### Scenario: Counter-rotation of nucleus

- **WHEN** cells orbit clockwise (positive angle change)
- **THEN** nucleus rotates counter-clockwise (negative angle change)
- **AND** nucleus rotation speed is 0.0003 rad/frame

---

### Requirement: Variable orbital speeds per cell

The system SHALL assign each cell a unique orbital speed within configurable range to create organic non-uniform motion.

#### Scenario: Default speed range assignment

- **WHEN** system initializes cells with default configuration
- **THEN** each cell speed is randomly assigned in range [0.0003, 0.0007]
- **AND** speeds create subtle relative motion between cells

#### Scenario: All cells orbit same direction

- **WHEN** orbital speeds are assigned
- **THEN** all speeds are positive (clockwise orbit)
- **AND** no cell orbits in reverse direction

#### Scenario: Slower speeds for calm effect

- **WHEN** system configures speed range to [0.0001, 0.0003]
- **THEN** cells rotate more slowly
- **AND** orbital period increases significantly

---

### Requirement: Radial distance from nucleus

The system SHALL calculate each cell's radial distance from nucleus center as normalized value [0.0, 1.0] where 1.0 = edge of available space.

#### Scenario: Baseline distance when silent

- **WHEN** energy is 0.0 (silence)
- **THEN** cells are at baseline distance 0.15 from nucleus
- **AND** cells appear merged with nucleus via metaball blur

#### Scenario: Expanded distance when loud

- **WHEN** energy is 1.0 (maximum audio)
- **THEN** cells are at maximum distance 0.75 from nucleus
- **AND** cells orbit independently with clear separation

#### Scenario: Intermediate distance with partial energy

- **WHEN** energy is 0.5 (moderate audio)
- **THEN** cells are at intermediate distance ~0.45 from nucleus
- **AND** partial merge/split behavior is visible

---

### Requirement: Polar to Cartesian coordinate conversion

The system SHALL convert polar coordinates (angle, distance) to Cartesian (x, y) for SVG rendering.

#### Scenario: Center at origin

- **WHEN** nucleus is at position (0, 0)
- **THEN** cell position calculates as (distance*cos(angle), distance*sin(angle))
- **AND** coordinates are relative to nucleus center

#### Scenario: Scale to viewBox pixels

- **WHEN** converting to pixel coordinates
- **THEN** multiply by nucleus radius and add viewBox center offset
- **AND** final position is absolute pixel location

#### Scenario: Y-axis flip for SVG

- **WHEN** rendering in SVG coordinate system
- **THEN** y-coordinate is inverted (SVG y increases downward)
- **AND** clockwise rotation appears correct visually

---

## How it INTERACTS (Integration)

### Requirement: Cell state data structure

The system SHALL maintain cell state array with position, velocity, and physics properties.

#### Scenario: Cell state interface

- **WHEN** cell state is accessed
- **THEN** each cell object contains: `{ id, angle, distance, velocity, speed, baseDistance, radius, color }`
- **AND** all values are numbers (no nested objects)

#### Scenario: Update all cells per frame

- **WHEN** animation frame triggers update
- **THEN** system iterates through all cells
- **AND** updates angle, distance, and radius for each

---

### Requirement: Energy-driven distance calculation

The system SHALL accept energy value from energy accumulator to determine target radial distance.

#### Scenario: Energy maps to distance

- **WHEN** energy value is provided (0.0 - 1.0)
- **THEN** target distance = baseDistance + (energy * maxExpansion)
- **AND** spring physics smoothly interpolates to target

#### Scenario: Zero energy collapses cells

- **WHEN** energy is 0.0
- **THEN** target distance equals baseDistance (0.15)
- **AND** cells collapse toward nucleus for merge effect
