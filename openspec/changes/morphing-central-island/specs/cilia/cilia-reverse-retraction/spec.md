# Spec: Cilia Reverse Retraction

Reverse animation (rewind effect) when user backspaces and cilia retract downward.

## Purpose

Define the timing, animation curve, and visual characteristics of cilia retraction during backspace action.

---

## How it LOOKS (Visual)

### Requirement: Cilia retract with reverse animation

The system SHALL animate cilia retracting downward when user backspaces.

#### Scenario: Single cilium retraction

- **WHEN** user backspaces one character
- **THEN** corresponding cilium retracts with reverse animation
- **AND** animation is: scale 1.0 → 0.5 → 0 (rewind effect)
- **AND** animation duration is 100ms (faster than extension)
- **AND** animation easing is ease-in (not spring-based)

#### Scenario: "Rewind" visual effect

- **WHEN** cilium retracts
- **THEN** cilium shrinks downward (toward divider)
- **AND** shrink appears as "playing animation backwards"
- **AND** hair texture shrinks with filament (maintains proportion)

#### Scenario: Last cilium retracts

- **WHEN** user backspaces last character
- **THEN** final cilium retracts completely
- **AND** paper display becomes empty (all characters removed)
- **AND** all cilia are now hidden (scale 0)

---

## How it WORKS (Behavioral)

### Requirement: Backspace triggers retraction

The system SHALL trigger reverse retraction when user backspaces.

#### Scenario: Backspace detection

- **WHEN** user presses Backspace key
- **THEN** system detects character removal from input
- **AND** system identifies which cilium corresponds to removed character
- **AND** that cilium performs reverse retraction animation

#### Scenario: Retraction is faster than extension

- **WHEN** comparing retraction to extension (hammer animation)
- **THEN** retraction is 100ms (vs 150ms for extension)
- **AND** retraction uses ease-in (vs spring for extension)
- **AND** this creates "quick erase" feel

#### Scenario: Multiple backspaces

- **WHEN** user holds Backspace key
- **THEN** cilia retract sequentially (right to left, reverse of typing order)
- **AND** each retraction is independent (not batched)
- **AND** paper display updates in real-time as cilia retract

---

## How it's LAYOUT (Positioning)

### Requirement: Retraction toward base point

The system SHALL animate cilium shrinking toward its base point on divider.

#### Scenario: Shrink to base

- **WHEN** cilium retracts
- **THEN** cilium shrinks toward base point (on divider line)
- **AND** transform origin is at base (same as extension)
- **AND** scale 1.0 → 0.5 → 0 (fully collapsed at base)

#### Scenario: Base point does not move

- **WHEN** cilium retracts
- **THEN** base point on divider does NOT move
- **AND** only cilium height/length changes
- **AND** divider remains stable throughout retraction
