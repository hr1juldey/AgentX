# Spec: Cell Dismiss Metaball Merge

Metaball merge effect when cell is absorbed into nucleus during dismiss gesture.

## Purpose

Define the metaball filter behavior and visual merge characteristics when cell contacts and is absorbed by nucleus.

---

## How it LOOKS (Visual)

### Requirement: Metaball merge on nucleus contact

The system SHALL apply metaball effect when cell contacts nucleus during dismiss.

#### Scenario: Cell contacts nucleus

- **WHEN** cell edge contacts nucleus edge (distance < nucleus radius + cell radius)
- **THEN** metaball merge activates immediately
- **AND** cell and nucleus appear as single organic blob
- **AND** boundaries between cell and nucleus are indistinguishable

#### Scenario: Cell partially absorbed

- **WHEN** cell is shrinking during absorption (scale 1.0 → 0.5)
- **THEN** metaball merge remains active throughout shrink
- **AND** cell appears to "melt" into nucleus
- **AND** merge creates smooth, organic absorption

---

## How it WORKS (Behavioral)

### Requirement: Metaball filter during dismiss

The system SHALL apply same metaball filter used for other elements during dismiss.

#### Scenario: Filter configuration

- **WHEN** cell dismiss is in progress
- **THEN** SVG metaball filter is already active (from sticky edges)
- **AND** filter configuration: blur 16px, alpha threshold matrix
- **AND** no additional filter setup required

#### Scenario: Filter scope

- **WHEN** metaball merge is active during dismiss
- **THEN** filter affects cell + nucleus (both elements)
- **AND** filter does NOT affect other cells (if present)
- **AND** this isolates dismiss to specific cell-nucleus pair

---

## How it's LAYOUT (Positioning)

### Requirement: Cell center aligns with nucleus center

The system SHALL position cell so its center aligns with nucleus center during dismiss.

#### Scenario: Alignment during absorption

- **WHEN** cell is being absorbed into nucleus
- **THEN** cell center moves toward nucleus center
- **AND** final position has cell center = nucleus center
- **AND** at this point, cell is fully overlapped by nucleus
