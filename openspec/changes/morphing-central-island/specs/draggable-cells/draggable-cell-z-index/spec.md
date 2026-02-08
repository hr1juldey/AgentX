# Spec: Draggable Cell Z-Index

Z-index layering for draggable cells to ensure proper stacking order during drag and at rest.

## Purpose

Define the z-index values and layering behavior that ensures dragged cells appear above other elements.

---

## How it LOOKS (Visual)

### Requirement: Dragged cell appears above all other cells

The system SHALL raise z-index of dragged cell so it appears above all other elements.

#### Scenario: Drag start z-index increase

- **WHEN** drag gesture begins (dragDistance > 5px)
- **THEN** cell z-index increases to 50
- **AND** cell appears above all other cells (which have z-index 10)
- **AND** cell appears above mode islands (if visible)

#### Scenario: Drag end z-index return

- **WHEN** drag gesture ends (mouse/touch release)
- **THEN** cell z-index returns to 10 (normal layer)
- **AND** cell no longer appears above other cells
- **AND** if cell overlaps other cells, normal stacking applies

#### Scenario: Multiple cells stacked

- **WHEN** multiple cells are at rest and overlap
- **THEN** cell with lower y-position appears above (natural stacking)
- **AND** all resting cells have z-index 10
- **AND** this creates "last moved = on top" behavior

---

## How it WORKS (Behavioral)

### Requirement: Z-index state management

The system SHALL manage z-index based on cell interaction state.

#### Scenario: Default z-index (at rest)

- **WHEN** cell is not being dragged
- **THEN** cell z-index is 10
- **AND** cell is in normal layer above background but below modals

#### Scenario: Dragging z-index

- **WHEN** cell is being dragged
- **THEN** cell z-index is 50
- **AND** cell is in top layer (above everything except toast notifications)

#### Scenario: Modal layer consideration

- **WHEN** modal overlay is displayed (not during drag)
- **THEN** modal has z-index 100 (above dragged cells)
- **AND** cells cannot be dragged while modal is open

---

## How it's LAYOUT (Positioning)

### Requirement: Z-index does not affect position

The system SHALL ensure z-index changes do not affect cell position.

#### Scenario: Z-index is purely visual layering

- **WHEN** z-index changes
- **THEN** cell position (x, y) does NOT change
- **AND** only visual stacking order changes
- **AND** this prevents layout shifts when z-index changes
