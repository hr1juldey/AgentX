# Spec: Chat Bar Keyboard Input

Bottom keyboard input section of chat bar that remains stable and accepts user text input.

## Purpose

Define the visual appearance, styling, and behavior of the keyboard input section at the bottom of the chat bar.

---

## How it LOOKS (Visual)

### Requirement: Stable input field at bottom

The system SHALL render input field at bottom of chat bar that accepts text input.

#### Scenario: Input field appearance

- **WHEN** chat bar is fully formed
- **THEN** keyboard section is bottom 50px of bar
- **AND** input field occupies full width (minus send button)
- **AND** input field has no border (integrated into bar)
- **AND** input background is `--color-membrane` (#141414 dark)

#### Scenario: Placeholder text

- **WHEN** input field is empty
- **THEN** placeholder text is "Type or speak your message..."
- **AND** placeholder color is `--color-vacuole` (#666666 gray)
- **AND** placeholder disappears when user types

#### Scenario: Send button

- **WHEN** send button is displayed
- **THEN** button is at right side of keyboard section
- **AND** button text is "Send"
- **AND** button background is `--color-actin` (#82AAFF blue)
- **AND** button text is `--color-nucleus` (#FFFFFF white)

---

## How it WORKS (Behavioral)

### Requirement: Input field handles typing

The system SHALL accept and display user text input.

#### Scenario: Typing triggers cilia

- **WHEN** user types in input field
- **THEN** each keystroke triggers cilia extension (see cilia specs)
- **AND** cilia transfer text from input to paper display
- **AND** input field shows what user is typing
- **AND** paper display shows same text (via cilia)

#### Scenario: Backspace handling

- **WHEN** user backspaces
- **THEN** last character is removed from input
- **AND** corresponding cilium retracts with reverse animation
- **AND** paper display updates (character disappears)

#### Scenario: Send action

- **WHEN** user clicks Send button or presses Enter
- **THEN** input clears
- **AND** cilia retract (all cilia disappear)
- **AND** paper clears
- **AND** message bubbles up and becomes floating cell (see sent-message-float spec)

---

## How it's LAYOUT (Positioning)

### Requirement: Input field layout

The system SHALL position input field and send button within keyboard section.

#### Scenario: Keyboard section dimensions

- **WHEN** keyboard section is rendered
- **THEN** section height is 50px (fixed)
- **THEN** section width equals bar width (400px desktop, 90% mobile)
- **AND** section has 25px border-radius on bottom corners only

#### Scenario: Input field layout

- **WHEN** input field is rendered
- **THEN** input field is at left side of keyboard section
- **AND** input field width = section width - send button width - padding
- **AND** input height = 50px - padding (full height minus internal padding)
- **AND** internal padding is 12px on left/right

#### Scenario: Send button layout

- **WHEN** send button is rendered
- **THEN** button is at right side of keyboard section
- **AND** button width is 60px (desktop) or 50px (mobile)
- **AND** button height matches section height (50px)
- **AND** button has 25px border-radius on right side only

#### Scenario: Text alignment

- **WHEN** input field displays text
- **THEN** text is left-aligned (padding-left: 12px)
- **AND** text is vertically centered (line-height: 50px)
- **AND** text color is `--color-nucleus` (#FFFFFF white)
- **AND** text does NOT overflow (scroll or truncate)
