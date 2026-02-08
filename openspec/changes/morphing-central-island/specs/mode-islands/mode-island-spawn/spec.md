# Spec: Mode Island Spawn

The graceful spawning animation of 4 mode islands (Voice, Chat, Camera, File) from the nucleus after longpress completes.

## Purpose

Define the timing, trajectory, and spring physics for mode island emergence from nucleus during the "graceful spill apart" animation.

---

## How it LOOKS (Visual)

### Requirement: 4 islands emerge from nucleus center

The system SHALL spawn 4 mode islands from nucleus center with smooth emergence animation.

#### Scenario: Island spawn from center

- **WHEN** longpress completes at 1500ms
- **THEN** 4 mode islands begin emerging from nucleus center
- **AND** islands spawn simultaneously (not sequentially)
- **AND** each island animates to its final cardinal position
- **AND** spawning is "graceful spill apart" (gentle separation, not explosive burst)

#### Scenario: Island appearance during spawn

- **WHEN** islands are spawning
- **THEN** islands scale from 0 → 1 during emergence
- **AND** islands have opacity 0 → 1 during emergence
- **AND** islands maintain circular shape throughout spawn
- **AND} spawn duration is ~200ms with spring physics

---

## How it WORKS (Behavioral)

### Requirement: Spring-physics emergence animation

The system SHALL use spring physics for organic island emergence.

#### Scenario: Spring configuration for spawn

- **WHEN** islands begin spawning
- **THEN** spring stiffness is 200
- **AND** spring damping is 25
- **AND** this creates smooth emergence with slight overshoot
- **AND** animation duration is approximately 200ms

#### Scenario: Spawn trajectory

- **WHEN** islands animate from nucleus center to cardinal positions
- **THEN** trajectory is direct line (not curved path)
- **AND** easing is spring-based (not cubic-bezier)
- **AND** islands may slightly overshoot final position then settle

#### Scenario: Spawn completion

- **WHEN** spawn animation completes (~200ms)
- **THEN** islands are fully opaque (opacity 1)
- **AND** islands are at full scale (scale 1)
- **AND** islands are at final cardinal positions
- **AND** islands become interactive (clickable, hoverable)

---

## How it's LAYOUT (Positioning)

### Requirement: Cardinal positioning around nucleus

The system SHALL position 4 islands in cardinal directions (Voice top, Chat left, File right, Camera bottom).

#### Scenario: Cardinal positions (desktop)

- **WHEN** islands spawn on desktop viewport
- **THEN** positions are:
  - Voice island: `top: -80px` from nucleus center (80px above)
  - Chat island: `left: -80px` from nucleus center (80px left)
  - File island: `right: -80px` from nucleus center (80px right)
  - Camera island: `bottom: -80px` from nucleus center (80px below)
- **AND** islands are 48px diameter each
- **AND** islands have 16px gap from nucleus edge

#### Scenario: Cardinal positions (mobile)

- **WHEN** islands spawn on mobile viewport (< 768px width)
- **THEN** positions are:
  - Voice island: `top: -60px` from nucleus center (60px above)
  - Chat island: `left: -60px` from nucleus center (60px left)
  - File island: `right: -60px` from nucleus center (60px right)
  - Camera island: `bottom: -60px` from nucleus center (60px below)
- **AND** islands are 40px diameter each (smaller for mobile)
- **AND** islands have 12px gap from nucleus edge

#### Scenario: Nucleus remains centered

- **WHEN** islands spawn around nucleus
- **THEN** nucleus position does NOT change
- **AND** nucleus remains at viewport center
- **AND** islands position relative to nucleus center (not viewport)
