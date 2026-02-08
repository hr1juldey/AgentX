# Spec: Mode Island Click Detection

Click interaction handling for mode islands that triggers sequential collapse into selected mode.

## Purpose

Define the precise click detection, timing, and trigger behavior when user selects a mode island.

---

## How it LOOKS (Visual)

### Requirement: Click feedback animation

The system SHALL provide visual feedback when user clicks mode island.

#### Scenario: Click scale feedback

- **WHEN** user clicks mode island
- **THEN** island scales from 1.0 → 0.95 → 1.0 (press effect)
- **AND** scale-down duration is 50ms
- **AND** scale-up duration is 100ms with spring bounce
- **AND** this provides tactile "button press" feedback

#### Scenario: Selected island highlight

- **WHEN** island is clicked and becomes selected mode
- **THEN** island icon rotates 360° over 300ms
- **AND** island background brightness increases by 20%
- **AND** island glow appears (box-shadow with mode color)
- **AND** this visual confirmation lasts until sequential collapse begins

---

## How it WORKS (Behavioral)

### Requirement: Click triggers sequential collapse

The system SHALL initiate sequential collapse animation when mode island is clicked.

#### Scenario: Click timing and trigger

- **WHEN** user clicks any mode island
- **THEN** system records which mode was selected (voice/chat/file/camera)
- **AND** system begins sequential collapse after 100ms delay
- **AND** delay allows user to see click feedback before islands start moving

#### Scenario: Prevent multiple clicks

- **WHEN** sequential collapse is in progress
- **THEN** additional island clicks are ignored
- **AND** first selected mode is locked in
- **AND** system does NOT switch to newly clicked mode

#### Scenario: Click vs drag distinction

- **WHEN** user drags island (not a quick click)
- **THEN** drag gesture takes precedence (see draggable cells spec)
- **AND** mode is NOT selected if drag distance > 5px
- **AND** this is the R014 bug fix (see draggable cells spec)

---

## How it's LAYOUT (Positioning)

### Requirement: Click interaction area

The system SHALL define clear click interaction area for each island.

#### Scenario: Click hitbox (desktop)

- **WHEN** user interacts with island on desktop
- **THEN** click hitbox is 48px diameter island circle
- **AND** entire island area is clickable
- **AND** click registers on mouse up (not mouse down)

#### Scenario: Touch hitbox (mobile)

- **WHEN** user interacts with island on mobile
- **THEN** touch hitbox is 56px diameter (44px minimum + padding)
- **AND** this accommodates finger touch targets
- **AND** visual island remains 40px, but hitbox extends

#### Scenario: Island spacing prevents misclicks

- **WHEN** all 4 islands are displayed
- **THEN** islands are spaced 160-180px apart (center-to-center)
- **AND** this prevents accidental clicks on neighboring islands
- **AND** gap between islands is at least 112px (desktop)
