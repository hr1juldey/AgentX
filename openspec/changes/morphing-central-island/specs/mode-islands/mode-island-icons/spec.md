# Spec: Mode Island Icons

Iconography for 4 mode islands (Voice microphone, Chat message bubble, File document, Camera lens).

## Purpose

Define the visual appearance, sizing, and animation behavior for mode island icons that identify each interaction mode.

---

## How it LOOKS (Visual)

### Requirement: Lucide React icons for each mode

The system SHALL render mode-specific icons from Lucide React icon library.

#### Scenario: Voice mode icon

- **WHEN** Voice mode island is rendered
- **THEN** island displays Mic icon from Lucide React
- **AND** icon color is `--color-nucleus` (#FFFFFF white)
- **AND** icon size is 24px (desktop) or 20px (mobile)
- **AND** icon is centered within island circle

#### Scenario: Chat mode icon

- **WHEN** Chat mode island is rendered
- **THEN** island displays MessageCircle icon from Lucide React
- **AND** icon color is `--color-nucleus` (#FFFFFF white)
- **AND** icon size is 24px (desktop) or 20px (mobile)
- **AND** icon is centered within island circle

#### Scenario: File mode icon

- **WHEN** File mode island is rendered
- **THEN** island displays FileText icon from Lucide React
- **AND** icon color is `--color-nucleus` (#FFFFFF white)
- **AND** icon size is 24px (desktop) or 20px (mobile)
- **AND** icon is centered within island circle

#### Scenario: Camera mode icon

- **WHEN** Camera mode island is rendered
- **THEN** island displays Camera icon from Lucide React
- **AND** icon color is `--color-nucleus` (#FFFFFF white)
- **AND** icon size is 24px (desktop) or 20px (mobile)
- **AND** icon is centered within island circle

---

## How it WORKS (Behavioral)

### Requirement: Icon animation on hover

The system SHALL apply subtle animation to icons when user hovers over mode islands.

#### Scenario: Hover scale animation

- **WHEN** user hovers over mode island
- **THEN** icon scales from 1.0 → 1.1 → 1.0 (subtle pulse)
- **AND** animation duration is 200ms
- **AND** animation easing is ease-out
- **AND** this draws attention to interactive nature of island

#### Scenario: Icon rotation on selected mode

- **WHEN** mode island is clicked (mode selected)
- **THEN** icon rotates 360° over 300ms before sequential collapse
- **AND** rotation indicates "confirmed selection"
- **AND** rotation easing is ease-in-out

---

## How it's LAYOUT (Positioning)

### Requirement: Icon centering within islands

The system SHALL position icons perfectly centered within mode island circles.

#### Scenario: Icon centering (desktop)

- **WHEN** icon renders within 48px diameter island
- **THEN** icon is positioned at `top: 50%, left: 50%, transform: translate(-50%, -50%)`
- **AND** icon maintains 24px size
- **AND** icon has 12px clearance from island edge on all sides

#### Scenario: Icon centering (mobile)

- **WHEN** icon renders within 40px diameter island
- **THEN** icon is positioned at `top: 50%, left: 50%, transform: translate(-50%, -50%)`
- **AND** icon maintains 20px size
- **AND** icon has 10px clearance from island edge on all sides

#### Scenario: Icon z-index layering

- **WHEN** icon is displayed within island
- **THEN** icon has z-index 2 (above island background)
- **AND** island background has z-index 1
- **AND** icon glow (active state) has z-index 3
