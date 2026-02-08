# Spec: Voice Cell Arrival Bounce

Bounce animation when voice cell arrives at its final force-layout position.

## Purpose

Define the bounce effect that provides visual confirmation when cell widget completes its journey and settles at final position.

---

## How it LOOKS (Visual)

### Requirement: Cell bounces once on arrival

The system SHALL animate cell with single bounce when it arrives at target position.

#### Scenario: Arrival bounce

- **WHEN** cell completes travel and reaches target position
- **THEN** cell performs single bounce
- **AND** bounce is scale 1.0 → 1.15 → 1.0
- **AND** bounce duration is 150ms
- **AND** bounce has 2 oscillation cycles (1.0 → 1.15 → 0.95 → 1.0)

#### Scenario: Settle to final state

- **WHEN** bounce completes
- **THEN** cell is at final position
- **AND** cell scale is 1.0 (baseline)
- **AND** cell becomes interactive (draggable, dismissible)
- **AND** cell enters "draggable but stable" state

---

## How it WORKS (Behavioral)

### Requirement: Spring bounce on arrival

The system SHALL trigger spring bounce when travel completes.

#### Scenario: Bounce trigger

- **WHEN** cell position is within 5px of target position
- **THEN** arrival is detected
- **AND** bounce animation triggers immediately
- **AND** bounce uses spring physics (stiffness 400, damping 15)

#### Scenario: Bounce energy

- **WHEN** bounce animation runs
- **THEN** initial overshoot is to scale 1.15 (15% larger)
- **AND** overshoot provides "I arrived!" feedback
- **AND** oscillation decay settles within 150ms

#### Scenario: No bounce on drag

- **WHEN** user drags cell after arrival
- **THEN** bounce does NOT retrigger on drag release
- **AND** cell simply settles at drag end position (no bounce)
- **AND** bounce only occurs on initial arrival from nucleus

---

## How it's LAYOUT (Positioning)

### Requirement: Bounce at target position

The system SHALL animate bounce while cell remains at target position.

#### Scenario: No position shift during bounce

- **WHEN** bounce animation is in progress
- **THEN** cell center position does NOT change
- **AND** only scale property animates
- **AND** cell grows/shrinks from center point

#### Scenario: Final position after bounce

- **WHEN** bounce completes
- **THEN** cell is at exact force-layout target position
- **AND** cell position does NOT shift after bounce
- **AND** cell is ready for drag interaction
