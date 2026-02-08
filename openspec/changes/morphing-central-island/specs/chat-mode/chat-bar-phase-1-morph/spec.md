# Spec: Chat Bar Phase 1 Morph

Phase 1 of chat bar morph: circle nucleus stretching horizontally to become 400px × 50px input bar.

## Purpose

Define the precise shape transformation, timing, and intermediate states for the circle-to-bar morph that is Phase 1 of chat mode activation.

---

## How it LOOKS (Visual)

### Requirement: Circle stretches to become bar

The system SHALL animate chat mode nucleus morphing from 60px circle to 400px × 50px bar.

#### Scenario: Initial circle state (Frame 0ms)

- **WHEN** Chat mode becomes active (sequential collapse complete)
- **THEN** nucleus is 60px diameter circle
- **AND** nucleus color is `--color-actin` (#82AAFF blue)
- **AND** nucleus is centered at viewport center

#### Scenario: Ellipse stretch (Frame 0-150ms)

- **WHEN** morph animation begins
- **THEN** nucleus stretches from circle to ellipse
- **AND** width animates: 60px → 200px → 400px (linear interpolation)
- **AND** height animates: 60px → 55px → 50px (slight shrink)
- **AND** border-radius animates: 30px → 27px → 25px

#### Scenario: Bar formation complete (Frame 150ms)

- **WHEN** ellipse stretch completes
- **THEN** nucleus is now 400px × 50px bar
- **AND** border-radius is 25px (fully rounded pill shape)
- **AND** bar maintains `--color-actin` blue background
- **AND** bar is centered horizontally at viewport center

#### Scenario: Smooth morph without artifacts

- **WHEN** morph animation is in progress
- **THEN** all properties animate simultaneously (width, height, border-radius)
- **AND** no visual distortion or artifacts occur
- **AND** morph appears organic and smooth

---

## How it WORKS (Behavioral)

### Requirement: Spring physics for morph

The system SHALL use spring physics for organic circle-to-bar transformation.

#### Scenario: Spring configuration

- **WHEN** morph animation runs
- **THEN** spring stiffness is 300
- **AND** spring damping is 30
- **AND** duration is approximately 150ms
- **AND** easing is spring-based (not cubic-bezier)

#### Scenario: Morph is Phase 1 only

- **WHEN** circle-to-bar morph completes
- **THEN** system waits 150ms before Phase 2 (paper emergence)
- **AND** during wait, bar is stable with no paper section
- **AND** Phase 2 is separate spec (paper-emergence)

#### Scenario: Morph triggers on chat mode selection

- **WHEN** user clicks Chat mode island
- **THEN** sequential collapse occurs (other islands merge into Chat)
- **AND** after sequential collapse, nucleus morph begins immediately
- **AND** no delay between collapse and morph

---

## How it's LAYOUT (Positioning)

### Requirement: Centered bar with constrained width

The system SHALL position morphed bar at viewport center with width constraint.

#### Scenario: Bar centering

- **WHEN** bar is fully formed
- **THEN** bar is positioned at `left: 50%, top: 50%, transform: translate(-50%, -50%)`
- **AND** bar does NOT shift vertically during morph (same center as circle)

#### Scenario: Bar width constraint

- **WHEN** bar is fully formed
- **THEN** bar width is 400px (constrained, not full viewport)
- **AND** on mobile (< 768px), bar width is 90% of viewport (max 400px)
- **AND** bar height is 50px (same on desktop and mobile)

#### Scenario: Border-radius becomes pill shape

- **WHEN** bar is fully formed
- **THEN** border-radius is 25px (half of bar height)
- **AND** this creates fully rounded pill/capsule shape
- **AND** all 4 corners have equal radius

#### Scenario: Z-index during morph

- **WHEN** morph is in progress
- **THEN** bar has z-index 10 (above background, below modals)
- **AND** mode islands are hidden by this point (sequential collapse complete)
