# Spec: Cilia Filament Hair Texture

Hair texture visual effect on cilia filaments that creates biological "typewriter hammer" appearance.

## Purpose

Define the visual appearance, rendering technique, and styling for hair texture on individual cilia filaments.

---

## How it LOOKS (Visual)

### Requirement: Hair texture on cilia filaments

The system SHALL render cilia with hair-like texture (not smooth lines).

#### Scenario: Filament appearance

- **WHEN** cilium is extended
- **THEN** filament has hair texture (not smooth line)
- **AND** hair texture appears as small fibers along main filament
- **AND** texture is subtle (visible on close inspection, not distracting)

#### Scenario: Hair texture implementation options

- **WHEN** rendering hair texture
- **THEN** use ONE of:
  - Option A: CSS background pattern (repeating-linear-gradient with hair lines)
  - Option B: SVG filter (turbulence + displacement for hair effect)
  - Option C: CSS mask-image with hair SVG pattern
  - Option D: Canvas drawing with procedural hair (fallback for mobile)
- **AND** choice depends on performance and browser compatibility

#### Scenario: Texture visibility

- **WHEN** cilia are fully extended
- **THEN** hair texture is visible on filament
- **AND** texture does not obscure filament shape
- **AND** texture color matches filament color (`--color-enzyme` cyan #00D9FF)

---

## How it WORKS (Behavioral)

### Requirement: Hair texture is decorative

The system SHALL apply hair texture as visual enhancement, not functional element.

#### Scenario: Texture does not affect animation

- **WHEN** cilia animate (extend/retract)
- **THEN** hair texture animates with filament
- **AND** texture does not slow down animation
- **AND** texture scales with filament (stretch, shrink)

#### Scenario: Texture performance

- **WHEN** multiple cilia have hair texture
- **THEN** rendering remains at 60 FPS
- **AND** texture is pre-rendered or GPU-accelerated (not real-time generated)
- **AND** fallback to smooth line if texture is too expensive

---

## How it's LAYOUT (Positioning)

### Requirement: Hair texture covers filament

The system SHALL position hair texture to cover entire filament surface.

#### Scenario: Texture coordinates

- **WHEN** hair texture is applied
- **THEN** texture covers filament from base (divider) to tip (paper)
- **AND** texture width is approximately 2-4px (filament width)
- **AND** texture height equals filament length (varies during animation)

#### Scenario: Texture scale

- **WHEN** filament animates (extends/retracts)
- **THEN** hair texture scales with filament
- **AND** texture does NOT distort or stretch disproportionately
- **AND** texture maintains aspect ratio
