# Spec: Sequential Collapse Metaball Merge

Metaball gooey merge effect when mode islands collide and combine during sequential collapse.

## Purpose

Define the metaball filter application and visual merge behavior when non-selected islands contact and merge into the selected island.

---

## How it LOOKS (Visual)

### Requirement: Gooey merge on island contact

The system SHALL apply metaball filter to create organic gooey merge when islands contact.

#### Scenario: Merge begins on contact

- **WHEN** sliding island contacts selected island
- **THEN** metaball merge effect activates immediately
- **AND** island boundaries blur together (no hard edge)
- **AND** gooey bridge connects islands during overlap
- **AND** merge appears organic like cell membranes fusing

#### Scenario: Partial merge during slide

- **WHEN** islands are partially overlapped during slide
- **THEN** thin gooey bridge connects islands
- **AND** bridge width varies with overlap amount
- **AND** bridge is thinnest at initial contact, thickest at full overlap

#### Scenario: Complete merge at full overlap

- **WHEN** islands are fully overlapped (centers aligned)
- **THEN** islands appear as single organic blob
- **AND** boundaries between islands are indistinguishable
- **AND** single blob takes on selected island's color

---

## How it WORKS (Behavioral)

### Requirement: SVG metaball filter application

The system SHALL apply SVG gaussian blur and color matrix filter for metaball effect.

#### Scenario: Filter configuration

- **WHEN** metaball merge is active
- **THEN** SVG filter is applied to island container group
- **AND** gaussian blur stdDeviation is 16px
- **AND** color matrix values are: "1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
- **AND** this creates sharp edges on blurred shapes (metaball effect)

#### Scenario: Filter scope

- **WHEN** sequential collapse is in progress
- **THEN** metaball filter is applied to ALL 4 islands (not per-island)
- **AND** single filter on parent `<g>` element
- **AND** all island children inherit filter effect
- **AND** this optimizes performance (single filter vs multiple)

#### Scenario: Filter activation timing

- **WHEN** first island begins sliding
- **THEN** metaball filter is activated immediately
- **AND** filter remains active throughout all 3 collapses
- **AND** filter deactivates after sequential collapse complete

### Requirement: Color blending during merge

The system SHALL blend island colors during metaball merge.

#### Scenario: Non-selected island color absorbed

- **WHEN** non-selected island merges into selected island
- **THEN** non-selected island's color is absorbed
- **AND** resulting blob takes on selected island's color
- **AND** color transition happens via metaball blur (smooth blend)

---

## How it's LAYOUT (Positioning)

### Requirement: ViewBox contains blur overflow

The system SHALL calculate ViewBox to prevent metaball blur from clipping at edges.

#### Scenario: ViewBox padding

- **WHEN** metaball filter is active
- **THEN** ViewBox padding is blur radius × 3 = 48px
- **AND** ViewBox extends 48px beyond outermost island position
- **AND** this prevents blur overflow from being clipped

#### Scenario: Dynamic ViewBox sizing

- **WHEN** islands move during collapse
- **THEN** ViewBox recalculates if island positions change significantly
- **AND** ViewBox always contains all islands + blur padding
- **AND** filter never clips island edges
