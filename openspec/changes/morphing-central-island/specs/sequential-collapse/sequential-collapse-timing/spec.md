# Spec: Sequential Collapse Timing

Timing and sequence order for mode islands merging into selected island during sequential collapse animation.

## Purpose

Define the precise timing, order, and duration of each island's merge into the selected mode island.

---

## How it LOOKS (Visual)

### Requirement: Sequential one-by-one collapse

The system SHALL collapse non-selected islands into selected island one at a time, not simultaneously.

#### Scenario: Collapse order when Voice selected

- **WHEN** Voice mode is selected (top island)
- **THEN** collapse sequence is:
  1. Chat island (left) slides toward Voice and merges (first)
  2. File island (right) slides toward Voice and merges (second)
  3. Camera island (bottom) slides toward Voice and merges (third)
- **AND** each merge is visible before next begins

#### Scenario: Collapse order when Chat selected

- **WHEN** Chat mode is selected (left island)
- **THEN** collapse sequence is:
  1. Voice island (top) slides toward Chat and merges (first)
  2. File island (right) slides toward Chat and merges (second)
  3. Camera island (bottom) slides toward Chat and merges (third)

#### Scenario: Collapse order for File/Camera

- **WHEN** File or Camera mode is selected
- **THEN** collapse sequence follows same pattern (3 non-selected islands merge one-by-one)
- **AND** order is: Voice → the other horizontal island → the remaining vertical island

---

## How it WORKS (Behavioral)

### Requirement: Timing between collapses

The system SHALL control timing between each island merge to create biological "engulfing" effect.

#### Scenario: Inter-collapse delay

- **WHEN** one island completes merge into selected island
- **THEN** system waits 150ms before starting next island merge
- **AND** this delay makes each engulfing action visible
- **AND** total collapse time for 3 islands is approximately 600-700ms

#### Scenario: Individual collapse duration

- **WHEN** single island slides toward selected island and merges
- **THEN** slide duration is 200ms with spring physics
- **AND** spring stiffness is 400 (snappy)
- **AND** spring damping is 20 (bouncy)
- **AND** merge occurs on contact (metaball effect)

#### Scenario: Sequential not parallel

- **WHEN** sequential collapse is in progress
- **THEN** only ONE island is moving at any given moment
- **AND** islands do NOT merge simultaneously
- **AND** this creates "cell engulfing one by one" biological metaphor

---

## How it's LAYOUT (Positioning)

### Requirement: Linear slide trajectory

The system SHALL slide non-selected islands directly toward selected island in straight line.

#### Scenario: Linear path (horizontal collapse)

- **WHEN** Chat island (left) merges into Voice island (top)
- **THEN** trajectory is diagonal line from left position to top position
- **AND** path is direct (not curved arc)
- **AND** island maintains scale 1 throughout slide

#### Scenario: Linear path (vertical collapse)

- **WHEN** Camera island (bottom) merges into Voice island (top)
- **THEN** trajectory is vertical line from bottom position to top position
- **AND** path is direct (not curved)
- **AND** island maintains scale 1 until contact

#### Scenario: Final position before merge

- **WHEN** island arrives at selected island position
- **THEN** island center aligns with selected island center
- **AND** islands overlap completely
- **AND** metaball merge effect activates (see separate spec)
