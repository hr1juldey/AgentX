# Spec: Draggable Cell Click vs Drag

Click versus drag detection for voice cells that fixes the R014 bug where onClick fired after drag.

## Purpose

Define the precise distance threshold and state tracking that distinguishes between click and drag gestures on draggable cells.

---

## How it LOOKS (Visual)

### Requirement: Visual feedback differs for click vs drag

The system SHALL provide different visual feedback depending on whether gesture is click or drag.

#### Scenario: Mouse down (both click and drag)

- **WHEN** user presses mouse button on cell
- **THEN** cell scales down to 0.95 (press effect)
- **AND** cursor changes to 'grabbing'
- **AND** cell z-index increases to 50 (above other cells)

#### Scenario: Drag visual feedback

- **WHEN** user moves mouse > 5px (drag threshold)
- **THEN** cell maintains scale 1.05 (slightly enlarged during drag)
- **AND** cursor remains 'grabbing'
- **AND** cell shadow appears (elevation effect)

#### Scenario: Click visual feedback

- **WHEN** user releases mouse before moving 5px
- **THEN** cell scales back to 1.0 (returns to normal)
- **AND** cursor returns to 'grab'
- **AND** cell performs brief "press confirmed" animation (scale 1.0 → 0.98 → 1.0)

---

## How it WORKS (Behavioral)

### Requirement: 5px distance threshold

The system SHALL track drag distance and distinguish click from drag based on 5px threshold.

#### Scenario: Distance tracking

- **WHEN** user presses mouse on cell
- **THEN** system records initial mouse position (mouseDown.x, mouseDown.y)
- **AND** system initializes dragDistance to 0
- **AND** system tracks current position during mouse move

#### Scenario: Drag threshold crossing

- **WHEN** dragDistance exceeds 5px
- **THEN** gesture is classified as DRAG (not click)
- **AND** drag functionality activates
- **AND** onClick handler will NOT fire on mouse up

#### Scenario: Click threshold (within 5px)

- **WHEN** user releases mouse with dragDistance < 5px
- **THEN** gesture is classified as CLICK
- **AND** onClick handler fires
- **AND** drag functionality does NOT activate

#### Scenario: R014 bug fix

- **WHEN** comparing to R014 implementation
- **THEN** this spec explicitly fixes R014 bug where onClick fired after drag
- **AND** R014 did NOT track dragDistance properly
- **AND** this implementation uses explicit distance tracking with threshold

---

## How it's LAYOUT (Positioning)

### Requirement: Mouse position calculation

The system SHALL calculate drag distance accurately from mouse movement.

#### Scenario: Euclidean distance calculation

- **WHEN** calculating drag distance
- **THEN** use Euclidean distance: `sqrt((currentX - startX)^2 + (currentY - startY)^2)`
- **AND** update dragDistance on every mouse move event
- **AND** compare dragDistance to 5px threshold

#### Scenario: Touch position calculation (mobile)

- **WHEN** user interacts via touch (mobile)
- **THEN** track touch position instead of mouse position
- **AND** use same 5px threshold
- **AND** touch position uses first touch point (multi-touch: ignore additional fingers)
