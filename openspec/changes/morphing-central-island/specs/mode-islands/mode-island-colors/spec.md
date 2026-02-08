# Spec: Mode Island Colors

Color scheme for 4 mode islands using C008 Organic UI design tokens for mode identification.

## Purpose

Define the precise color values and semantic meanings for each mode island's appearance in idle, hover, and active states.

---

## How it LOOKS (Visual)

### Requirement: Mode-specific accent colors from C008 tokens

The system SHALL render each mode island with unique accent color from Organic UI design system.

#### Scenario: Voice island color

- **WHEN** Voice mode island is rendered
- **THEN** island background color is `--color-endoplasmic` (HSL 270 60% 70%, #C792EA purple)
- **AND** island icon color is `--color-nucleus` (#FFFFFF white)
- **AND** island hover state uses same purple with 10% brightness increase
- **AND** island active state uses `--color-golgi` (HSL 50 100% 50%, #FFD700 gold) accent

#### Scenario: Chat island color

- **WHEN** Chat mode island is rendered
- **THEN** island background color is `--color-actin` (HSL 220 70% 73%, #82AAFF blue)
- **AND** island icon color is `--color-nucleus` (#FFFFFF white)
- **AND** island hover state uses same blue with 10% brightness increase
- **AND** island active state uses `--color-enzyme` (HSL 187 100% 50%, #00D9FF cyan) accent

#### Scenario: File island color

- **WHEN** File mode island is rendered
- **THEN** island background color is `--color-microtubule` (HSL 164 100% 67%, #64FFDA green)
- **AND** island icon color is `--color-nucleus` (#FFFFFF white)
- **AND** island hover state uses same green with 10% brightness increase
- **AND** island active state uses `--color-enzyme` (HSL 187 100% 50%, #00D9FF cyan) accent

#### Scenario: Camera island color

- **WHEN** Camera mode island is rendered
- **THEN** island background color is `--color-mitochondria` (HSL 17 90% 60%, #FF6B35 orange)
- **AND** island icon color is `--color-nucleus` (#FFFFFF white)
- **AND** island hover state uses same orange with 10% brightness increase
- **AND** island active state uses `--color-lysosome` (HSL 4 90% 63%, #FF4757 red) accent

---

## How it WORKS (Behavioral)

### Requirement: Color state transitions

The system SHALL smoothly transition between color states when user interacts with islands.

#### Scenario: Idle to hover transition

- **WHEN** user hovers over mode island
- **THEN** island background color transitions to hover state
- **AND** transition duration is 150ms
- **AND** transition easing is ease-out (smooth, not abrupt)
- **AND** icon color remains white throughout

#### Scenario: Hover to active transition

- **WHEN** user clicks mode island (selecting mode)
- **THEN** island background color transitions to active state
- **AND** transition duration is 100ms (faster than hover)
- **AND** accent color (gold, cyan, cyan, red) appears as icon glow
- **AND** this indicates "selected" state before sequential collapse

#### Scenario: Sequential collapse color blending

- **WHEN** sequential collapse begins (non-selected islands merge into selected)
- **THEN** island colors blend via metaball merge effect
- **AND** resulting nucleus color is selected mode's color
- **AND** non-selected island colors are absorbed into selected color

---

## How it's LAYOUT (Positioning)

### Requirement: Color-based visual hierarchy

The system SHALL use color to establish visual hierarchy among mode islands.

#### Scenario: Color distinguishes modes

- **WHEN** all 4 islands are displayed simultaneously
- **THEN** each island's unique color clearly distinguishes it from others
- **AND** colors have sufficient contrast (no two islands look similar)
- **AND** color blindness is accommodated (icons + colors)

#### Scenario: Nucleus color reflects selected mode

- **WHEN** mode is selected (sequential collapse complete)
- **THEN** nucleus takes on selected mode's color
- **AND** Voice: purple nucleus, Chat: blue nucleus, File: green nucleus, Camera: orange nucleus
- **AND** nucleus maintains this color until mode is dismissed

#### Scenario: Dark mode compatibility

- **WHEN** system is in dark mode (default void background)
- **THEN** all mode island colors remain vibrant (no darkening)
- **AND** colors are specified as HSL with high lightness (60-73%)
- **AND** colors maintain contrast against `--color-void` (#0A0A0A) background
