# Spec: Longpress Cancel Detection

Detection and handling of cancel conditions during longpress gesture to prevent accidental mode spawning.

## Purpose

Define the precise conditions that cancel an in-progress longpress, ensuring users can easily abort the gesture without triggering mode selection.

---

## How it LOOKS (Visual)

### Requirement: Visual feedback during cancel

The system SHALL provide visual feedback when user moves away from nucleus during longpress.

#### Scenario: Approaching cancel threshold

- **WHEN** user moves cursor/finger 25-50px away from nucleus center during longpress
- **THEN** nucleus glow begins fading (opacity 50% → 0%)
- **AND** pulse animation slows (indicating cancel is imminent)
- **AND** visual feedback is smooth (not abrupt)

#### Scenario: Cancel complete feedback

- **WHEN** user moves beyond 50px threshold
- **THEN** nucleus immediately returns to idle appearance
- **AND** any accumulated glow fades out within 100ms
- **AND** pulse animation resumes idle rhythm (3000ms duration)

---

## How it WORKS (Behavioral)

### Requirement: 50px distance cancel threshold

The system SHALL cancel longpress when user moves 50px or more away from nucleus center.

#### Scenario: Distance-based cancel

- **WHEN** user's cursor/finger position is ≥ 50px from nucleus center
- **THEN** longpress is cancelled
- **AND** timer resets to 0
- **AND** nucleus returns to idle state
- **AND** mode islands do NOT spawn

#### Scenario: Re-enter before cancel

- **WHEN** user moves 30-49px away, then returns within 30px
- **THEN** longpress continues (not cancelled)
- **AND** timer continues from where it left off
- **AND** visual intensity returns to longpress level

#### Scenario: Rapid movement handling

- **WHEN** user moves cursor/finger rapidly (jittery movement)
- **THEN** system uses smoothed position (5-pixel moving average)
- **AND** cancel threshold is based on smoothed position (prevents accidental cancel)

### Requirement: Click free space cancels longpress

The system SHALL cancel longpress if user clicks/taps arbitrary free space (not on nucleus or mode islands).

#### Scenario: Free space click during longpress

- **WHEN** user clicks anywhere on viewport except nucleus during longpress
- **THEN** longpress is cancelled
- **AND** timer resets
- **AND** nucleus returns to idle state

#### Scenario: Free space click after mode spawn

- **WHEN** mode islands are visible and user clicks free space
- **THEN** longpress cancel does NOT apply (mode selection is active)
- **AND** click outside islands triggers mode dismiss (returns to idle)
- **AND** all islands fade out and nucleus returns to idle

---

## How it's LAYOUT (Positioning)

### Requirement: Cancel zone around nucleus

The system SHALL define a clear cancel zone that prevents accidental mode spawning.

#### Scenario: Cancel zone radius

- **WHEN** longpress is in progress
- **THEN** cancel zone is circle with 50px radius from nucleus center
- **AND** this is approximately nucleus radius + 20px buffer
- **AND** cancel zone is not visually marked (invisible boundary)

#### Scenario: Interaction area vs cancel zone

- **WHEN** user interacts with nucleus
- **THEN** interaction area for starting longpress is 120px diameter (60px radius)
- **AND** cancel zone during longpress is 100px diameter (50px radius)
- **AND** this creates 10px buffer where user can move without cancelling

#### Scenario: Mobile touch handling

- **WHEN** user touches with multiple fingers during longpress
- **THEN** system tracks primary finger (first touch point)
- **AND** cancel zone is calculated from primary finger position
- **AND** secondary fingers are ignored for cancel detection
