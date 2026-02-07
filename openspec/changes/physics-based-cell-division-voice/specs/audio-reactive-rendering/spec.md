# Spec: Audio-Reactive Rendering

SVG rendering system that updates cell visuals at 60 FPS based on audio energy and physics state.

## Purpose

Render physics-calculated cell positions and sizes to SVG with metaball filter, updating smoothly in response to audio input.

---

## How it LOOKS (Visual)

### Requirement: Smooth 60 FPS rendering

The system SHALL render cell animations at approximately 60 frames per second for fluid motion.

#### Scenario: Continuous smooth animation

- **WHEN** audio is active and cells are orbiting
- **THEN** rendering updates ~60 times per second
- **AND** motion appears fluid without stuttering
- **AND** no visible frame drops

#### Scenario: Responsive to energy changes

- **WHEN** audio level changes rapidly
- **THEN** visual updates reflect changes smoothly
- **AND** no sudden jumps or glitches in animation

---

### Requirement: Color scheme consistency

The system SHALL use design token colors for nucleus and cells with consistent theming.

#### Scenario: Purple accent theme

- **WHEN** system renders with default theme
- **THEN** nucleus uses primary purple color (#8B5CF6)
- **AND** cells use same color with opacity variation
- **AND** colors match overall app design tokens

#### Scenario: Dark mode compatibility

- **WHEN** system renders in dark mode
- **THEN** colors remain visible against dark background
- **AND** metaball filter produces correct dark-on-light effect

#### Scenario: Optional cell color variation

- **WHEN** system configures per-cell colors
- **THEN** each cell may have subtle hue variation
- **AND** variation creates visual interest while maintaining harmony

---

## How it WORKS (Behavioral)

### Requirement: SVG coordinate system

The system SHALL render cells in SVG viewBox coordinate system centered at origin.

#### Scenario: Centered origin

- **WHEN** SVG viewBox is defined
- **THEN** center point (0, 0) is at nucleus center
- **AND** coordinates extend equally in all directions
- **AND** cells are positioned relative to center

#### Scenario: ViewBox scales to content

- **WHEN** SVG viewBox is calculated
- **THEN** viewBox size accommodates max cell reach + blur padding
- **AND** viewBox is square (equal width and height)
- **AND** no cells are clipped at edges

---

### Requirement: Circle element rendering

The system SHALL render each cell and nucleus as SVG `<circle>` elements.

#### Scenario: Nucleus circle

- **WHEN** nucleus is rendered
- **THEN** `<circle cx="0" cy="0" r="{nucleusRadius}" />`
- **AND** circle is centered at origin
- **AND** radius matches design token (160 desktop, 72 mobile)

#### Scenario: Cell circles

- **WHEN** cells are rendered
- **THEN** each cell has `<circle cx="{x}" cy="{y}" r="{radius}" />`
- **AND** coordinates calculated from polar position
- **AND** radius scaled by energy and breathing

#### Scenario: Element reuse for performance

- **WHEN** cells update position each frame
- **THEN** existing `<circle>` elements update attributes
- **AND** no elements are destroyed/recreated unnecessarily
- **AND** rendering is optimized

---

### Requirement: Filter application

The system SHALL apply metaball filter to SVG group containing all circles.

#### Scenario: Filter on group element

- **WHEN** SVG structure is created
- **THEN** `<g filter="url(#goo-physics-cells)">` wraps all circles
- **AND** filter is defined once in `<defs>`
- **AND** all circles inherit filter effect

#### Scenario: Filter performance optimization

- **WHEN** rendering at 60 FPS
- **THEN** filter calculation doesn't cause frame drops
- **AND** GPU acceleration is utilized if available
- **AND** filter is applied once per frame (not per element)

---

### Requirement: Responsive sizing

The system SHALL adjust viewBox and element sizes based on viewport (mobile vs desktop).

#### Scenario: Desktop sizing

- **WHEN** viewport width >= 768px
- **THEN** nucleus radius is 160px
- **AND** cell base radius is 20-40px
- **AND** blur radius is 16px

#### Scenario: Mobile sizing

- **WHEN** viewport width < 768px
- **THEN** nucleus radius is 72px
- **AND** cell base radius is 12-24px
- **AND** blur radius is 12px

#### Scenario: Responsive updates

- **WHEN** viewport size changes
- **THEN** component recalculates sizes
- **AND** animation continues smoothly at new size

---

## How it INTERACTS (Integration)

### Requirement: Render loop integration

The system SHALL integrate with requestAnimationFrame loop for efficient updates.

#### Scenario: Frame-by-frame updates

- **WHEN** requestAnimationFrame callback fires
- **THEN** system queries latest cell positions from orbit physics
- **AND** system updates SVG circle attributes
- **AND** system schedules next frame

#### Scenario: Pause when inactive

- **WHEN** component unmounts or tab is inactive
- **THEN** render loop cancels requestAnimationFrame
- **AND** no updates occur until reactivation

---

### Requirement: Physics state consumption

The system SHALL consume cell state array from orbit physics system for rendering.

#### Scenario: Read cell positions

- **WHEN** render frame executes
- **THEN** system reads: `[{ x, y, radius, color }, ...]`
- **AND** system converts to SVG circle attributes
- **AND** system doesn't modify physics state (read-only)

#### Scenario: Handle empty cell array

- **WHEN** physics system returns empty array
- **THEN** system renders nucleus only
- **AND** no errors occur from missing cells

---

### Requirement: Component props API

The system SHALL accept configuration props for customization.

#### Scenario: Cell count prop

- **WHEN** component receives `cellCount={12}`
- **THEN** system renders 12 orbiting cells
- **AND** physics system creates 12 cell states

#### Scenario: Blur prop override

- **WHEN** component receives `blur={20}`
- **THEN** system uses custom blur radius
- **AND** metaball effect strength changes accordingly

#### Scenario: Debug mode prop

- **WHEN** component receives `debug={true}`
- **THEN** system renders energy bar indicator
- **AND** system displays numeric state values
