# Spec: Chat Bar Horizontal Divider

Horizontal divider that separates paper display (top) from keyboard input (bottom) and holds cilia.

## Purpose

Define the visual appearance, positioning, and cilia attachment function of the horizontal divider in chat bar structure.

---

## How it LOOKS (Visual)

### Requirement: 1px horizontal line between sections

The system SHALL render 1px horizontal divider separating paper and keyboard sections.

#### Scenario: Divider appearance

- **WHEN** chat bar is fully formed
- **THEN** divider is 1px horizontal line
- **AND** divider color is `--color-membrane` (#141414)
- **AND** divider spans full width of chat bar
- **AND** divider is positioned between paper (top) and keyboard (bottom)

#### Scenario: Cilia attach to divider

- **WHEN** cilia are extended (user is typing)
- **THEN** cilia filaments extend UPWARD from divider
- **AND** cilia base points are anchored along divider line
- **AND** cilia appear to "grow from" divider

---

## How it WORKS (Behavioral)

### Requirement: Divider holds cilia base points

The system SHALL anchor cilia filaments to divider line.

#### Scenario: Cilia anchor points

- **WHEN** cilia emerge during typing
- **THEN** each cilium's base point is on divider line
- **AND** base point x-coordinate corresponds to character position
- **AND** cilium extends upward (toward paper display)
- **AND** divider does NOT move when cilia extend

#### Scenario: Divider is structural

- **WHEN** chat bar is interacted with
- **THEN** divider position is fixed (does NOT animate)
- **AND** only cilia animate (divider is stable)
- **AND** this creates "keyboard is stable, cilia move" metaphor

---

## How it's LAYOUT (Positioning)

### Requirement: Divider positioned between sections

The system SHALL position divider between paper display and keyboard input sections.

#### Scenario: Divider vertical position

- **WHEN** chat bar is fully formed
- **THEN** divider is below paper section
- **AND** divider is above keyboard section
- **AND** divider position is: `top: paper height, left: 0, right: 0`

#### Scenario: Divider spans full width

- **WHEN** divider is rendered
- **THEN** divider width = bar width (400px desktop, 90% mobile)
- **AND** divider height = 1px
- **AND** divider has no border-radius (full-width line)

#### Scenario: Cilia spacing along divider

- **WHEN** multiple cilia are extended
- **THEN** cilia are evenly spaced along divider
- **AND** spacing is approximately 12px between cilia base points
- **AND** cilia align with character positions in input field
