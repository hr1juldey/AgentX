# Spec: Voice Cell Force Layout

D3-force simulation for auto-positioning voice cells in circle around nucleus with dynamic radius based on cell count.

## Purpose

Define the force configuration, radius calculation, and positioning behavior for auto-arranging voice cells in circle pattern around nucleus.

---

## How it LOOKS (Visual)

### Requirement: Cells arranged in circle around nucleus

The system SHALL position cells in circle around nucleus using force-directed layout.

#### Scenario: 1-4 cells - small circle

- **WHEN** 1-4 cells are present
- **THEN** force layout radius is 160px
- **AND** cells are evenly distributed around circle
- **AND** cells have approximately equal angular spacing (360° / cell count)

#### Scenario: 5-8 cells - medium circle

- **WHEN** 5-8 cells are present
- **THEN** force layout radius is 200px
- **AND** cells are evenly distributed around larger circle
- **AND** cells have more spacing between them

#### Scenario: 9-12 cells - large circle

- **WHEN** 9-12 cells are present
- **THEN** force layout radius is 240px
- **AND** cells are evenly distributed around largest circle
- **AND** cells have maximum spacing to prevent overcrowding

---

## How it WORKS (Behavioral)

### Requirement: D3-force simulation configuration

The system SHALL use specific force parameters for circle layout.

#### Scenario: Force parameters

- **WHEN** force layout runs
- **THEN** radial force strength is 0.8 (pulls cells toward circle radius)
- **AND** charge force strength is -50 (pushes cells apart from each other)
- **AND** collide force strength is (cell radius + 8) (prevents overlap)
- **AND** center force strength is 0.1 (keeps layout centered on nucleus)

#### Scenario: Simulation execution

- **WHEN** force layout runs
- **THEN** simulation runs for 300 ticks (iterations)
- **AND** positions are calculated and stored
- **AND** simulation does NOT run continuously (only on cell count change)

#### Scenario: Memoization for performance

- **WHEN** force layout calculates positions
- **THEN** positions are memoized (cached) until cell count changes
- **AND** repeated calls with same cell count return cached positions
- **AND** this prevents unnecessary recalculations

---

## How it's LAYOUT (Positioning)

### Requirement: Center around nucleus

The system SHALL position cells in circle centered on nucleus position.

#### Scenario: Center point

- **WHEN** force layout calculates positions
- **THEN** center point is nucleus center coordinates
- **AND** all cell positions are relative to nucleus center
- **AND** nucleus is at (0, 0) in force layout coordinate system

#### Scenario: Position calculation

- **WHEN** force layout completes
- **THEN** each cell has position: `{ x: nucleus.x + radius * cos(angle), y: nucleus.y + radius * sin(angle) }`
- **AND** positions are rounded to integers (no subpixel positioning)
- **AND** positions are returned as Record<string, { x, y }>

#### Scenario: Mobile radius adjustment

- **WHEN** force layout runs on mobile viewport
- **THEN** all radius values are multiplied by 0.75 (scale down)
- **AND** 1-4 cells: 120px, 5-8 cells: 150px, 9-12 cells: 180px
- **AND** this accommodates smaller mobile screens
