# Spec: Chat Bar Phase 2 Paper Emerge

Phase 2 of chat bar morph: paper section expanding upward from horizontal divider.

## Purpose

Define the timing, animation, and structure of the paper section that emerges from the chat bar after Phase 1 morph completes.

---

## How it LOOKS (Visual)

### Requirement: Paper section expands upward

The system SHALL animate paper section expanding upward from horizontal divider.

#### Scenario: Paper emergence begins (Frame 300ms)

- **WHEN** Phase 1 (circle-to-bar) completes and 150ms wait elapses
- **THEN** paper section begins expanding upward from divider
- **AND** initial paper height is 0px (hidden/collapsed)
- **AND** paper expands to 100px height (auto-adjusts based on content)

#### Scenario: Paper structure

- **WHEN** paper section is visible
- **THEN** paper is top section of chat bar
- **AND** paper background is `--color-cell` (#1E1E1E dark)
- **AND** paper shows current input only (not full chat history)
- **AND** paper is initially empty/hidden until user types

#### Scenario: Cilia emerge from divider

- **WHEN** paper section expansion completes
- **THEN** cilia are positioned along divider (horizontal line)
- **AND** cilia extend upward from divider (not from keyboard section)
- **AND** cilia are hidden until user types (see cilia specs)

---

## How it WORKS (Behavioral)

### Requirement: Two-phase emergence with delay

The system SHALL separate bar morph (Phase 1) and paper emergence (Phase 2) with timing delay.

#### Scenario: Phase sequence

- **WHEN** Chat mode activates
- **THEN** Phase 1: Circle → bar morph (0-150ms)
- **AND** Wait: 150ms delay (bar stable, no paper)
- **AND** Phase 2: Paper expands upward (300-450ms)
- **AND** Total morph time: 450ms

#### Scenario: Paper expansion animation

- **WHEN** paper emergence begins
- **THEN** spring stiffness is 250
- **AND** spring damping is 25
- **AND** expansion duration is approximately 150ms
- **AND** easing is spring-based (smooth expansion)

#### Scenario: Paper content appears

- **WHEN** paper section is fully expanded
- **THEN** paper is initially empty (no content)
- **AND** paper content appears when user types (see cilia specs)
- **AND** paper shows CURRENT INPUT only (not chat history)

---

## How it's LAYOUT (Positioning)

### Requirement: Paper sits above divider

The system SHALL position paper section above horizontal divider in chat bar structure.

#### Scenario: Chat bar vertical structure

- **WHEN** chat bar is fully formed
- **THEN** top section: Paper display (0-100px height, auto-adjusts)
- **AND** middle: Horizontal divider (1px height)
- **AND** bottom section: Keyboard input (50px height)
- **AND** total bar height = paper height + 1px + 50px

#### Scenario: Paper expansion from divider

- **WHEN** paper emerges
- **THEN** paper expands upward from divider line
- **AND** divider stays at fixed position (does NOT move)
- **AND** keyboard section stays at fixed position (does NOT move)

#### Scenario: Paper width matches bar

- **WHEN** paper section expands
- **THEN** paper width equals bar width (400px desktop, 90% mobile)
- **AND** paper border-radius matches bar (25px top corners only)
- **AND** paper has sharp bottom corners (meets divider flatly)
