# Spec: Cell Dismiss Nucleus Absorb

Nucleus absorption animation and elastic bounce when cell is fully dismissed and absorbed.

## Purpose

Define the cell shrink animation, nucleus absorption behavior, and elastic bounce completion for the dismiss gesture.

---

## How it LOOKS (Visual)

### Requirement: Cell shrinks and nucleus absorbs

The system SHALL animate cell shrinking while nucleus absorbs it with elastic bounce.

#### Scenario: Cell shrink sequence

- **WHEN** cell contacts nucleus during dismiss
- **THEN** cell shrinks: scale 1.0 → 0.5 → 0
- **AND** shrink duration is 300ms with spring physics
- **AND** cell opacity fades: 1.0 → 0.5 → 0

#### Scenario: Nucleus absorption

- **WHEN** cell is shrinking into nucleus
- **THEN** nucleus scale increases: 1.0 → 1.2 → 1.0 (elastic bounce)
- **AND** nucleus duration is 200ms
- **AND** bounce has 2 oscillation cycles before settling

#### Scenario: Dismiss complete

- **WHEN** absorption animation completes
- **THEN** cell is removed from DOM
- **AND** nucleus returns to idle state (scale 1.0, normal pulse)
- **AND** nucleus color remains purple (voice mode color)

---

## How it WORKS (Behavioral)

### Requirement: Spring physics for absorption

The system SHALL use spring physics for organic absorption animation.

#### Scenario: Cell shrink spring

- **WHEN** cell shrink begins
- **THEN** spring stiffness is 300
- **AND** spring damping is 25
- **AND** this creates smooth shrink with slight settle

#### Scenario: Nucleus bounce spring

- **WHEN** nucleus absorbs cell
- **THEN** spring stiffness is 400
- **AND** spring damping is 20
- **AND** this creates elastic "digesting" bounce

#### Scenario: Timing coordination

- **WHEN** dismiss sequence runs
- **THEN** cell shrink and nucleus bounce occur simultaneously
- **AND** both animations start when cell contacts nucleus
- **AND** cell disappears (opacity 0) as nucleus completes bounce

---

## How it's LAYOUT (Positioning)

### Requirement: Absorption at center

The system SHALL position cell at nucleus center during absorption.

#### Scenario: Center alignment

- **WHEN** cell is absorbed
- **THEN** cell center aligns with nucleus center
- **AND** cell shrinks from center point (not from corner)
- **AND** nucleus bounces in place (does not move)

#### Scenario: Final state

- **WHEN** absorption completes
- **THEN** nucleus remains at original position
- **AND** nucleus is only cell in view (dismissed cell removed)
- **AND** force layout recalculates for remaining cells (if any)
