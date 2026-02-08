# Spec: Nucleus Morph Circle to Bar

Circle-to-bar morph animation when Chat mode is selected (nucleus stretches horizontally to become chat input bar).

## Purpose

Define the precise shape transformation, timing, and intermediate states when nucleus morphs from circular 60px to 400px × 50px bar for Chat mode.

---

## How it LOOKS (Visual)

### Requirement: Circle stretches horizontally to become bar

The system SHALL animate nucleus morphing from circle to horizontal bar with rounded corners.

#### Scenario: Initial circle state

- **WHEN** Chat mode is selected (sequential collapse complete)
- **THEN** nucleus is initially 60px diameter circle
- **AND** nucleus color is `--color-actin` (#82AAFF blue)
- **AND** nucleus is centered at viewport position

#### Scenario: Ellipse stretch phase (0-150ms)

- **WHEN** morph animation begins
- **THEN** nucleus stretches from circle to ellipse
- **AND** width animates: 60px → 200px → 400px
- **AND** height animates: 60px → 55px → 50px
- **AND** animation duration is 150ms total
- **AND** easing is spring-based (stiffness 300, damping 30)

#### Scenario: Bar formation complete (150-300ms)

- **WHEN** ellipse stretch completes
- **THEN** nucleus is now 400px × 50px bar
- **AND** border-radius morphs to 25px (fully rounded pill shape)
- **AND** bar maintains `--color-actin` blue background
- **AND** bar is centered horizontally at viewport center

#### Scenario: Smooth morph without distortion

- **WHEN** morph animation is in progress
- **THEN** border-radius animates smoothly (circle 30px → pill 25px)
- **AND** no visual distortion or artifacts occur
- **AND** morph appears organic (not mechanical)

---

## How it WORKS (Behavioral)

### Requirement: Two-phase morph with delay

The system SHALL morph in two phases with delay between circle→bar and bar→paper.

#### Scenario: Phase 1 - Circle to bar only

- **WHEN** Chat mode becomes active after sequential collapse
- **THEN** Phase 1 morph begins immediately
- **AND** only circle→bar transformation occurs
- **AND** NO paper section yet (that's Phase 2)
- **AND** Phase 1 duration is 150ms

#### Scenario: Phase 2 - Paper emerges after bar

- **WHEN** Phase 1 completes (bar formed)
- **THEN** system waits 150ms before Phase 2
- **AND** Phase 2 is paper section expanding upward (see separate spec)
- **AND** total morph time = 150ms (bar) + 150ms (wait) + 150ms (paper) = 450ms

#### Scenario: Morph uses spring physics

- **WHEN** morph animation runs
- **THEN** spring stiffness is 300
- **AND** spring damping is 30
- **AND** this creates smooth morph with minimal overshoot
- **AND** animation is ease-out (fast start, slow finish)

---

## How it's LAYOUT (Positioning)

### Requirement: Centered bar with constrained width

The system SHALL position morphed bar at viewport center with maximum width constraint.

#### Scenario: Bar centering

- **WHEN** nucleus morphs to bar
- **THEN** bar is positioned at `left: 50%, transform: translateX(-50%)`
- **AND** bar vertical position is same as original nucleus center
- **AND** bar does NOT shift vertically during morph

#### Scenario: Bar width constraint

- **WHEN** bar is fully formed
- **THEN** bar width is 400px (constrained, not full viewport)
- **AND** bar height is 50px
- **AND** on mobile (< 768px), bar width is 90% of viewport (max 400px)
- **AND** bar never exceeds 400px width

#### Scenario: Bar border-radius

- **WHEN** bar is fully formed
- **THEN** border-radius is 25px (half of bar height)
- **AND** this creates fully rounded pill shape
- **AND** corner radius is consistent on all 4 corners

#### Scenario: Z-index during morph

- **WHEN** morph is in progress
- **THEN** bar has z-index 10 (above other elements)
- **AND** mode islands are hidden by this point (sequential collapse complete)
- **AND** bar does not overlap with important UI elements
