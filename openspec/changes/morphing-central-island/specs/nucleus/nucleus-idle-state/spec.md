# Spec: Nucleus Idle State

The idle state appearance and behavior of the central nucleus when no user interaction is active.

## Purpose

Define the visual and behavioral characteristics of the central nucleus in its default idle state, establishing the baseline from which all other states (longpress, mode selection, mode active) transition.

---

## How it LOOKS (Visual)

### Requirement: Circular nucleus with subtle pulse

The system SHALL render a circular nucleus with subtle breathing pulse animation when in idle state.

#### Scenario: Desktop idle nucleus

- **WHEN** system is in idle state on desktop viewport
- **THEN** nucleus is rendered as circle with 60px diameter
- **AND** nucleus background color is `--color-nucleus` (#FFFFFF white)
- **AND** nucleus has subtle pulse animation (scale 1.0 → 1.05 → 1.0)
- **AND** pulse animation duration is 3000ms (3 seconds)
- **AND** pulse easing is cubic-bezier(0.4, 0, 0.6, 1) for smooth "breathing"
- **AND** nucleus is centered in viewport (fixed positioning, bottom-1/4 of screen height)

#### Scenario: Mobile idle nucleus

- **WHEN** system is in idle state on mobile viewport (< 768px width)
- **THEN** nucleus is rendered as circle with 48px diameter (20% smaller)
- **AND** all other visual characteristics match desktop idle state

#### Scenario: Pulse animation smoothness

- **WHEN** pulse animation is running
- **THEN** animation runs at 60 FPS without jank
- **AND** animation is GPU-accelerated using CSS transforms (scale property only)

---

## How it WORKS (Behavioral)

### Requirement: Idle state detection and activation

The system SHALL detect when nucleus should be in idle state and activate idle animations.

#### Scenario: Initialize in idle state

- **WHEN** component first mounts
- **THEN** nucleus state is set to 'idle'
- **AND** pulse animation begins immediately
- **AND** no other islands or widgets are visible

#### Scenario: Return to idle after mode dismiss

- **WHEN** user dismisses active mode (drags cell to center in voice mode, or cancels chat mode)
- **THEN** nucleus transitions back to idle state
- **AND** pulse animation resumes after 300ms delay
- **AND** all mode-specific elements fade out before idle state activates

#### Scenario: Prevent idle during active interaction

- **WHEN** user is actively interacting (longpress in progress, mode active, dragging)
- **THEN** idle state is NOT activated
- **AND** pulse animation is paused

### Requirement: Pulse animation lifecycle

The system SHALL manage pulse animation lifecycle efficiently to prevent performance issues.

#### Scenario: Pulse animation loop

- **WHEN** idle state is active
- **THEN** pulse animation loops infinitely
- **AND** animation does not accumulate memory over time
- **AND** animation pauses when tab is not visible (Page Visibility API)

#### Scenario: Pulse animation on low-power devices

- **WHEN** device battery is low or power-saving mode is active
- **THEN** pulse animation duration increases to 6000ms (slower breathing)
- **AND** animation remains smooth (no frame drops)

---

## How it's LAYOUT (Positioning)

### Requirement: Centered nucleus positioning

The system SHALL position nucleus in center of viewport with consistent spacing.

#### Scenario: Desktop positioning

- **WHEN** nucleus renders on desktop viewport
- **THEN** nucleus is positioned fixed at `bottom: 25%, left: 50%, transform: translateX(-50%)`
- **AND** nucleus maintains 60px diameter
- **AND** nucleus has 16px minimum clearance from viewport edges

#### Scenario: Mobile positioning

- **WHEN** nucleus renders on mobile viewport
- **THEN** nucleus is positioned fixed at `bottom: 30%, left: 50%, transform: translateX(-50%)`
- **AND** nucleus maintains 48px diameter
- **AND** nucleus has 12px minimum clearance from viewport edges

#### Scenario: Viewport resize handling

- **WHEN** viewport resizes between mobile and desktop breakpoints
- **THEN** nucleus smoothly transitions to new size and position
- **AND** transition uses spring physics (stiffness 300, damping 30)
- **AND** transition duration is approximately 150ms
