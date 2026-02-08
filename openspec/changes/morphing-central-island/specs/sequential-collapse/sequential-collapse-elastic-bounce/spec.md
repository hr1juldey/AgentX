# Spec: Sequential Collapse Elastic Bounce

Elastic bounce animation on selected island after each island is absorbed during sequential collapse.

## Purpose

Define the bounce effect that provides visual feedback when an island is absorbed, confirming the biological "engulfing" metaphor.

---

## How it LOOKS (Visual)

### Requirement: Nucleus bounces after each absorption

The system SHALL animate selected island with elastic bounce after each non-selected island merges into it.

#### Scenario: Bounce after first merge

- **WHEN** first island (e.g., Chat) completes merge into selected island (e.g., Voice)
- **THEN** selected island performs elastic bounce
- **AND** bounce is scale 1.0 → 1.15 → 1.0
- **AND** bounce duration is 150ms
- **AND** bounce has 2-3 oscillation cycles before settling

#### Scenario: Bounce after second merge

- **WHEN** second island (e.g., File) completes merge into selected island
- **THEN** selected island performs another elastic bounce
- **AND** bounce parameters match first bounce (scale 1.0 → 1.15 → 1.0)
- **AND** bounce occurs after 150ms inter-collapse delay

#### Scenario: Bounce after third (final) merge

- **WHEN** third island (e.g., Camera) completes merge into selected island
- **THEN** selected island performs final elastic bounce
- **AND** bounce is slightly larger (scale 1.0 → 1.2 → 1.0) to indicate completion
- **AND** bounce duration is 200ms (slightly longer for emphasis)

---

## How it WORKS (Behavioral)

### Requirement: Spring bounce configuration

The system SHALL use spring physics for elastic bounce after absorption.

#### Scenario: Spring stiffness and damping for bounce

- **WHEN** bounce animation triggers
- **THEN** spring stiffness is 500 (very snappy)
- **AND** spring damping is 15 (very low damping = oscillating)
- **AND** this creates sharp "pop" with multiple oscillations
- **AND** oscillations decay within 150-200ms

#### Scenario: Bounce timing relative to merge

- **WHEN** island completes merge (centers aligned, metaball active)
- **THEN** bounce begins immediately (no delay)
- **AND** bounce provides "digesting the absorbed island" feedback
- **AND** user sees: merge → bounce → brief pause → next merge

#### Scenario: Energy dissipation

- **WHEN** bounce oscillations occur
- **THEN** each oscillation is smaller than previous (decaying amplitude)
- **AND** first oscillation is scale 1.15 (or 1.2 for final)
- **AND** second oscillation is scale 1.05
- **AND** third oscillation is scale 1.01 (near baseline)
- **AND** animation settles at scale 1.0

---

## How it's LAYOUT (Positioning)

### Requirement: Bounce at center position

The system SHALL animate bounce while selected island remains at center position.

#### Scenario: No position shift during bounce

- **WHEN** bounce animation is in progress
- **THEN** island center position does NOT change
- **AND** only scale property animates
- **AND** island grows/shrinks from center point (not top-left anchored)

#### Scenario: Bounce does not affect layout

- **WHEN** island bounces (scale increases)
- **THEN** bounce does NOT push other elements away
- **AND** bounce is purely visual (does not affect layout flow)
- **AND** this is achieved via CSS transform (scale vs width/height)
