# Spec: Metaball Merge Behavior

Visual merge/split behavior of cells based on radial distance from nucleus using SVG blur filter.

## Purpose

Create organic "gooey" merging effect where cells combine with nucleus when close and separate when far apart, using SVG gaussian blur and color matrix filter.

---

## How it LOOKS (Visual)

### Requirement: Metaball merge effect

The system SHALL render cells and nucleus with metaball filter that creates organic merging when shapes overlap.

#### Scenario: Cells merged at low energy

- **WHEN** energy is 0.0 and cells are at distance 0.15
- **THEN** cells and nucleus appear as single organic blob
- **AND** boundaries between cells are indistinguishable
- **AND** shape morphs smoothly as cells orbit

#### Scenario: Cells partially merged at medium energy

- **WHEN** energy is 0.5 and cells are at distance 0.45
- **THEN** cells are partially separated from nucleus
- **AND** thin gooey bridges connect cells to nucleus
- **AND** bridges stretch and break as cells orbit

#### Scenario: Cells fully split at high energy

- **WHEN** energy is 1.0 and cells are at distance 0.75
- **THEN** cells are fully separated from nucleus
- **AND** each cell is distinct with no connection to nucleus
- **AND** metaball effect is only visible if cells overlap each other

---

### Requirement: Blur-based merge threshold

The system SHALL use blur radius to determine merge threshold distance.

#### Scenario: Merge threshold at blur/2

- **WHEN** cell distance from nucleus < blur radius / 2
- **THEN** cell appears merged with nucleus
- **AND** boundaries are completely blurred together

#### Scenario: Split threshold at blur*2

- **WHEN** cell distance from nucleus > blur radius * 2
- **THEN** cell appears fully separated
- **AND** no visible connection between shapes

#### Scenario: Transition zone at blur to blur*2

- **WHEN** cell distance is between blur and blur*2
- **THEN** thin gooey bridge connects cell to nucleus
- **AND** bridge width varies smoothly with distance

---

## How it WORKS (Behavioral)

### Requirement: SVG gaussian blur filter

The system SHALL apply feGaussianBlur filter to all cells and nucleus with configurable stdDeviation.

#### Scenario: Default blur radius

- **WHEN** system initializes with desktop configuration
- **THEN** blur stdDeviation is 16 pixels
- **AND** blur creates soft edges on all shapes

#### Scenario: Mobile blur radius

- **WHEN** system initializes with mobile configuration
- **THEN** blur stdDeviation is 12 pixels
- **AND** smaller blur accommodates smaller viewBox

#### Scenario: Blur strength affects merge distance

- **WHEN** blur radius is increased to 24
- **THEN** merge threshold increases proportionally
- **AND** cells merge at greater distances

---

### Requirement: Color matrix thresholding

The system SHALL apply feColorMatrix filter to sharpen blurred edges and create solid shapes.

#### Scenario: Alpha thresholding

- **WHEN** color matrix is applied to blurred output
- **THEN** alpha values below threshold become transparent
- **AND** alpha values above threshold become opaque
- **AND** creates sharp edges on merged shapes

#### Scenario: Standard metaball matrix

- **WHEN** system uses default color matrix
- **THEN** matrix values are: "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
- **AND** this produces standard metaball effect

#### Scenario: Adjustable threshold

- **WHEN** color matrix alpha multiplier is increased
- **THEN** merge threshold becomes more aggressive
- **AND** shapes merge at lower blur overlap

---

### Requirement: Dynamic cell radius based on energy

The system SHALL scale cell radius based on energy level to enhance merge/split visual effect.

#### Scenario: Cells shrink when merged

- **WHEN** energy is 0.0 and cells are merged
- **THEN** cell radius scales to 0.8x base size
- **AND** smaller cells contribute to "merged into nucleus" appearance

#### Scenario: Cells expand when split

- **WHEN** energy is 1.0 and cells are separated
- **THEN** cell radius scales to 1.4x base size
- **AND** larger cells are more visible when orbiting independently

#### Scenario: Breathing animation

- **WHEN** cells are at any energy level
- **THEN** subtle sine wave scales radius by ±10%
- **AND** breathing creates "alive" organic feel

---

## How it INTERACTS (Integration)

### Requirement: Filter application to SVG group

The system SHALL apply metaball filter to SVG group containing nucleus and all cells.

#### Scenario: Single filter on group

- **WHEN** SVG is rendered
- **THEN** filter is applied once to parent `<g>` element
- **AND** all children inherit the filter effect
- **AND** performance is optimized (single filter vs multiple)

#### Scenario: Filter ID for isolation

- **WHEN** multiple components exist on page
- **THEN** each component uses unique filter ID
- **AND** filter IDs are namespaced (e.g., "goo-physics-cells")

---

### Requirement: ViewBox sizing for filter safety

The system SHALL calculate viewBox to accommodate blur overflow without clipping.

#### Scenario: ViewBox padding for blur

- **WHEN** viewBox is calculated
- **THEN** padding = blur radius * 3
- **AND** viewBox size = (maxReach + padding) * 2
- **AND** blur overflow is fully contained

#### Scenario: Responsive viewBox sizing

- **WHEN** cell count or max distance changes
- **THEN** viewBox recalculates accordingly
- **AND** filter never clips cell edges
