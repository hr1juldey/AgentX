# Spec: Draggable Cell Viewport Bounds

Viewport boundary constraints that prevent draggable cells from being dragged off-screen.

## Purpose

Define the boundary checking and constraint behavior that keeps draggable cells within visible viewport area.

---

## How it LOOKS (Visual)

### Requirement: Cells cannot leave viewport

The system SHALL prevent cells from being dragged beyond viewport edges.

#### Scenario: Drag to edge

- **WHEN** user drags cell toward viewport edge
- **THEN** cell stops at viewport edge (does not continue beyond)
- **AND** cell edge aligns with viewport edge
- **AND** user can continue dragging along edge (but not beyond)

#### Scenario: Drag beyond edge attempt

- **WHEN** user drags cursor beyond viewport edge
- **THEN** cell remains at viewport edge
- **AND** cell does NOT follow cursor beyond edge
- **AND** cursor can move beyond, but cell is constrained

---

## How it WORKS (Behavioral)

### Requirement: Boundary calculation

The system SHALL calculate viewport boundaries and constrain cell position.

#### Scenario: Boundary edges

- **WHEN** calculating viewport boundaries
- **THEN** left boundary: `0px` (viewport left edge)
- **AND** right boundary: `viewportWidth - cellWidth`
- **AND** top boundary: `0px` (viewport top edge)
- **AND** bottom boundary: `viewportHeight - cellHeight`

#### Scenario: Position constraint

- **WHEN** cell position is updated during drag
- **THEN** system clamps position to boundary range
- **AND** formula: `x = Math.max(0, Math.min(x, viewportWidth - cellWidth))`
- **AND** formula: `y = Math.max(0, Math.min(y, viewportHeight - cellHeight))`
- **AND** clamping occurs every frame during drag

#### Scenario: Resize handling

- **WHEN** viewport resizes while cell is near edge
- **THEN** cell position is adjusted to stay within new boundaries
- **AND** if new boundary would exclude cell, cell is clamped inside
- **AND** adjustment happens smoothly (no teleportation)

---

## How it's LAYOUT (Positioning)

### Requirement: Minimum clearance from edges

The system SHALL ensure cells maintain minimum clearance from viewport edges.

#### Scenario: Clearance calculation

- **WHEN** cell is positioned near viewport edge
- **THEN** minimum clearance is 0px (cell can touch edge)
- **AND** cell can extend to exact edge (not required to have padding)
- **AND** this maximizes available drag area

#### Scenario: Safe zone during drag

- **WHEN** cell is being dragged
- **THEN** entire cell must remain within viewport
- **AND** no part of cell can extend beyond viewport
- **AND** this ensures cell is always fully visible and interactive
