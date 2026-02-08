# Spec: Voice Cell Sticky Edges

Metaball sticky edge behavior when voice cells are close to each other or nucleus.

## Purpose

Define the metaball merge effect and distance threshold that causes cells to stick together with gooey connection.

---

## How it LOOKS (Visual)

### Requirement: Cells merge when close together

The system SHALL apply metaball effect when cells are within threshold distance.

#### Scenario: Cell-to-cell sticky edges

- **WHEN** two cells are within 40px of each other
- **THEN** metaball merge activates between cells
- **AND** gooey bridge connects cells
- **AND** bridge width varies with distance (closer = thicker bridge)
- **AND** cells appear to stick together like biological cells

#### Scenario: Cell-to-nucleus sticky edges

- **WHEN** cell is within 40px of voice mode nucleus
- **THEN** metaball merge activates between cell and nucleus
- **AND** gooey bridge connects cell to nucleus
- **AND** this creates "returning to parent" visual feedback

#### Scenario: Multiple cells in cluster

- **WHEN** 3+ cells are close together (all within 40px of each other)
- **THEN** all cells merge via metaball effect
- **AND** cluster appears as single organic blob with multiple nuclei
- **AND** this creates "cell colony" appearance

---

## How it WORKS (Behavioral)

### Requirement: Distance-based sticky threshold

The system SHALL activate metaball merge when cells are within threshold distance.

#### Scenario: Sticky threshold distance

- **WHEN** distance between cell centers is calculated
- **THEN** sticky threshold is 40px (desktop) or 32px (mobile)
- **AND** threshold = (cell radius × 2) + 16px buffer
- **AND** when distance < threshold, metaball activates

#### Scenario: Metaball filter application

- **WHEN** any cells are within sticky threshold
- **THEN** SVG metaball filter is applied to cell container
- **AND** filter affects all cells equally (not per-cell filtering)
- **AND** filter configuration matches nucleus metaball (blur 16px, alpha threshold matrix)

#### Scenario: Dynamic sticky calculation

- **WHEN** cells are moving (during drag or emergence)
- **THEN** sticky distance is recalculated every frame
- **AND** metaball activates/deactivates smoothly as cells move
- **AND** no abrupt transitions in sticky state

---

## How it's LAYOUT (Positioning)

### Requirement: Cell positions trigger sticky

The system SHALL calculate cell positions to determine sticky state.

#### Scenario: Distance calculation

- **WHEN** checking if cells should stick
- **THEN** calculate Euclidean distance: `sqrt((x2-x1)^2 + (y2-y1)^2)`
- **AND** compare distance to threshold (40px or 32px)
- **AND** if distance < threshold, activate metaball

#### Scenario: Force layout respects sticky

- **WHEN** force layout calculates positions
- **THEN** layout ensures cells are NOT within sticky threshold initially
- **AND** cells are positioned with minimum 60px spacing
- **AND** only user drag brings cells close enough to stick
