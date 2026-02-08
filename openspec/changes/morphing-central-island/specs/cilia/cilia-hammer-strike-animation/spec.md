# Spec: Cilia Hammer Strike Animation

Per-keystroke hammer-strike animation for each cilium extension with "cchunk + bounce" effect.

## Purpose

Define the timing, spring configuration, and visual characteristics of the hammer-strike animation that simulates typewriter hammer hitting paper.

---

## How it LOOKS (Visual)

### Requirement: Hammer-strike animation per keystroke

The system SHALL animate each cilium with hammer-strike motion when corresponding character is typed.

#### Scenario: Hammer animation sequence

- **WHEN** user types a character
- **THEN** corresponding cilium performs hammer-strike animation
- **AND** animation is: scale 0 → 1.2 → 1.0 (cchunk + bounce)
- **AND** animation duration is 150ms total
- **AND** animation has 2 phases: scale-up (100ms) + bounce settle (50ms)

#### Scenario: "Cchunk" effect

- **WHEN** hammer animation begins
- **THEN** cilium snaps upward quickly (scale 0 → 1.2)
- **AND** scale-up phase is 100ms
- **AND** this creates "sharp strike" visual effect

#### Scenario: Bounce settle

- **WHEN** cilium reaches scale 1.2
- **THEN** cilium settles back to scale 1.0
- **AND** settle phase is 50ms with spring bounce
- **AND** bounce may have 1-2 small oscillations before settling

---

## How it WORKS (Behavioral)

### Requirement: Spring configuration for hammer

The system SHALL use spring physics for snappy hammer-strike animation.

#### Scenario: Spring stiffness and damping

- **WHEN** hammer animation runs
- **THEN** spring stiffness is 400 (very snappy)
- **AND** spring damping is 20 (low damping = bouncy)
- **AND** this creates quick scale-up with elastic bounce

#### Scenario: One hammer per keystroke

- **WHEN** user types character
- **THEN** exactly one cilium performs hammer animation
- **AND** cilium corresponds to character position in input
- **AND** previous cilia do NOT re-animating (they stay extended)

#### Scenario: Sequential hammers

- **WHEN** user types multiple characters quickly
- **THEN** each character triggers its own hammer animation
- **AND** animations are sequential (left to right)
- **AND** animations do NOT interfere with each other

---

## How it's LAYOUT (Positioning)

### Requirement: Hammer animates in place

The system SHALL animate cilium scale without position change.

#### Scenario: Scale-only animation

- **WHEN** hammer animation runs
- **THEN** cilium x/y position does NOT change
- **AND** only scale property animates
- **AND** cilium extends from base point (divider) upward

#### Scenario: Animation origin at base

- **WHEN** cilium scales during hammer animation
- **THEN** transform origin is at base (divider line)
- **AND** cilium grows upward from base
- **AND** scale 0 = collapsed (invisible), scale 1.2 = extended
