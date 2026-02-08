# Spec: Draggable Cell Drag Physics

Spring physics and motion characteristics for draggable cells during user drag gesture.

## Purpose

Define the visual behavior, spring configuration, and responsiveness of cells while being dragged by user.

---

## How it LOOKS (Visual)

### Requirement: Cell follows cursor with spring attachment

The system SHALL animate cell following cursor during drag with spring physics.

#### Scenario: Drag start

- **WHEN** drag gesture begins (dragDistance > 5px)
- **THEN** cell scales to 1.05 (slight enlargement)
- **AND** cell shadow appears (box-shadow: 0 10px 30px rgba(0,0,0,0.3))
- **AND** cell z-index increases to 50 (above all other elements)
- **AND** cursor changes to 'grabbing'

#### Scenario: Drag in progress

- **WHEN** user is dragging cell
- **THEN** cell position updates every frame to follow cursor
- **AND** cell follows cursor with slight delay (spring lag, not 1:1)
- **AND** spring lag creates "weighty" feeling
- **AND** cell maintains scale 1.05 and shadow during drag

#### Scenario: Drag end

- **WHEN** user releases mouse/touch to end drag
- **THEN** cell settles at final position
- **AND** cell scale returns to 1.0
- **AND** cell shadow disappears
- **AND** cell z-index returns to normal (10)

---

## How it WORKS (Behavioral)

### Requirement: Spring physics during drag

The system SHALL use spring physics for cursor following during drag.

#### Scenario: Spring configuration for drag

- **WHEN** drag is in progress
- **THEN** spring stiffness is 600 (very responsive, minimal lag)
- **AND** spring damping is 30 (slightly underdamped for smooth motion)
- **AND** this creates tight cursor following with minimal overshoot

#### Scenario: Frame updates during drag

- **WHEN** user moves cursor during drag
- **THEN** cell position updates every frame (60 FPS)
- **AND** position is calculated via spring physics: `target - current * stiffness`
- **AND** updates use requestAnimationFrame for smooth motion

#### Scenario: Drag constraints

- **WHEN** cell is being dragged
- **THEN** cell can be dragged anywhere within viewport
- **AND** cell does NOT snap to grid or positions
- **AND** cell position is unconstrained (free movement)

---

## How it's LAYOUT (Positioning)

### Requirement: Cell center follows cursor

The system SHALL position cell so its center follows cursor position.

#### Scenario: Center-to-cursor positioning

- **WHEN** drag is in progress
- **THEN** cell center is positioned at cursor coordinates
- **AND** formula: `cell.x = cursor.x - (cell.width / 2)`
- **AND** formula: `cell.y = cursor.y - (cell.height / 2)`
- **AND** this makes cell appear "grabbed at center"

#### Scenario: Offset from initial click

- **WHEN** drag begins
- **THEN** system calculates offset from cell center to click point
- **AND** offset is maintained throughout drag
- **AND** cell does NOT "snap" center to cursor (keeps initial grab point)

#### Scenario: Touch offset (mobile)

- **WHEN** drag occurs via touch on mobile
- **THEN** touch offset is calculated from touch point to cell center
- **AND** offset is maintained throughout drag
- **AND** cell follows finger with same offset as desktop
