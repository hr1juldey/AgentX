# Spec: Sent Message Float

Transition behavior when sent message bubbles up and becomes floating draggable cell in voice mode layout.

## Purpose

Define the animation, timing, and state transition when sent message transforms from chat input to floating cell widget.

---

## How it LOOKS (Visual)

### Requirement: Message bubbles up and becomes cell

The system SHALL animate sent message bubbling up from chat bar and transforming into floating cell.

#### Scenario: Send trigger

- **WHEN** user clicks Send button (or presses Enter)
- **THEN** input text is captured as message
- **AND** chat bar clears (input + paper + cilia all disappear)
- **AND** message begins floating upward from chat bar position

#### Scenario: Bubble up animation

- **WHEN** message floats upward
- **THEN** message translates: `translateY(+20px)` with ease-out
- **AND** message moves away from chat bar (not attached anymore)
- **AND** animation duration is 200ms

#### Scenario: Morph to cell

- **WHEN** message completes bubble-up animation
- **THEN** message morphs into cell widget appearance
- **AND** message gains border, shadow, metaball-ready styling
- **AND** message becomes indistinguishable from voice mode cells

#### Scenario: Auto-position in circle

- **WHEN** message becomes cell
- **THEN** force layout calculates position in circle around nucleus
- **AND** cell animates to calculated position (spring trajectory)
- **AND** cell settles with bounce animation (see voice-cell-arrival-bounce spec)

---

## How it WORKS (Behavioral)

### Requirement: State transition from chat to voice cell

The system SHALL transition sent message from chat mode to voice mode cell.

#### Scenario: Mode context switch

- **WHEN** message is sent from chat mode
- **THEN** message transitions to voice mode context
- **AND** message becomes draggable (like other voice cells)
- **AND** message is dismissible via drag-to-center (like other voice cells)

#### Scenario: Chat mode remains active

- **WHEN** message is sent and becomes cell
- **THEN** chat bar reappears (empty, ready for new input)
- **AND** user can continue typing and sending messages
- **AND** each sent message becomes another floating cell

#### Scenario: Multiple sent messages

- **WHEN** user sends multiple messages
- **THEN** each message becomes independent floating cell
- **AND** all cells are positioned via force layout
- **AND** cells can be dragged and dismissed independently

---

## How it's LAYOUT (Positioning)

### Requirement: Cell joins force layout circle

The system SHALL position sent message cell in circle around nucleus using force layout.

#### Scenario: Position calculation

- **WHEN** message becomes cell
- **THEN** force layout includes new cell in calculation
- **AND** cell is assigned position in circle (160/200/240px radius based on count)
- **AND** cell animates from chat bar position to calculated position

#### Scenario: Chat bar position reference

- **WHEN** bubble-up animation begins
- **THEN** start position is chat bar center
- **AND** end position is force-layout calculated position
- **AND** trajectory is direct line (not curved path)

#### Scenario: Z-index during transition

- **WHEN** message transitions to cell
- **THEN** message has z-index 20 (above chat bar, below cells)
- **AND** after transition, cell has z-index 10 (normal cell layer)
