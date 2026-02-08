# Spec: Chat Bar Send Button

Send button in keyboard section that triggers message send action and converts input to floating cell.

## Purpose

Define the visual appearance, interaction behavior, and send trigger for the Send button in chat bar.

---

## How it LOOKS (Visual)

### Requirement: Send button at right of keyboard section

The system SHALL render Send button at right side of keyboard input section.

#### Scenario: Button appearance

- **WHEN** chat bar is fully formed
- **THEN** Send button is at right side of keyboard section
- **AND** button width is 60px (desktop) or 50px (mobile)
- **AND** button height equals section height (50px)
- **AND** button background is `--color-actin` (#82AAFF blue)
- **AND** button text is "Send" in `--color-nucleus` (#FFFFFF white)

#### Scenario: Button hover state

- **WHEN** user hovers over Send button
- **THEN** button brightness increases by 10%
- **AND** cursor changes to 'pointer'
- **AND** transition duration is 150ms

#### Scenario: Button disabled state

- **WHEN** input field is empty
- **THEN** Send button is disabled (opacity 0.5)
- **AND** cursor is 'not-allowed'
- **AND** click does NOT trigger send

---

## How it WORKS (Behavioral)

### Requirement: Send button triggers message send

The system SHALL trigger send action when user clicks Send button.

#### Scenario: Send action

- **WHEN** user clicks Send button (and input is not empty)
- **THEN** input text is captured
- **AND** input field clears
- **AND** all cilia retract (see cilia-reverse-retraction spec)
- **AND** paper display clears
- **AND** message bubbles up and becomes floating cell (see sent-message-float spec)

#### Scenario: Enter key shortcut

- **WHEN** user presses Enter key in input field
- **THEN** same action as clicking Send button
- **AND** this is keyboard shortcut for send

#### Scenario: Prevent empty send

- **WHEN** user clicks Send button but input is empty
- **THEN** send action does NOT trigger
- **AND** button shows disabled state (opacity 0.5)
- **AND** no message cell is created

---

## How it's LAYOUT (Positioning)

### Requirement: Button positioned at right edge

The system SHALL position Send button at right side of keyboard section.

#### Scenario: Button positioning

- **WHEN** Send button is rendered
- **THEN** button is at right side of keyboard section
- **AND** button is `position: absolute, right: 0, top: 0`
- **AND** button height equals section height (50px)
- **AND** button has 25px border-radius on right corners only

#### Scenario: Button spacing

- **WHEN** Send button is positioned
- **THEN** button has 8px margin from right edge of section
- **AND** button does NOT touch section edge
- **AND** this provides visual breathing room
