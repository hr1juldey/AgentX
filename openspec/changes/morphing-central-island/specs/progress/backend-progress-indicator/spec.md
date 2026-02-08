# Spec: Backend Progress Indicator

Metaball-based progress ring with orbiting circles that appears when backend agents are processing (LangGraph thinking, STT processing, widget generation).

## Purpose

Define the visual appearance, animation behavior, and display conditions for the backend progress indicator ported from the Kotlin ProgressLoader component.

---

## How it LOOKS (Visual)

### Requirement: Metaball progress ring with rotating arc and orbiting circles

The system SHALL display a metaball-wrapped progress ring with rotating arc and 9 orbiting circles when backend is processing.

#### Scenario: Progress ring structure

- **WHEN** backend progress indicator is displayed
- **THEN** progress ring is centered in nucleus (or active mode nucleus)
- **AND** ring consists of:
  - 1 rotating arc (215° sweep angle)
  - 9 small circles (50px diameter each) orbiting around
  - All elements wrapped in metaball filter (blur radius 40px)
- **AND** base color is `--color-enzyme` (#00D9FF cyan)
- **AND** arc and circles are `--color-nucleus` (#FFFFFF white)

#### Scenario: Progress ring size

- **WHEN** progress ring displays in standard nucleus
- **THEN** overall container size is 300px × 300px
- **AND** rotating arc size is 250px diameter
- **AND** orbiting circles are 50px diameter each
- **AND** on mobile, all sizes scale to 80% (240px, 200px, 40px)

#### Scenario: Metaball merge effect

- **WHEN** arc and circles overlap during orbit
- **THEN** elements merge via metaball filter (gooey effect)
- **AND** blur radius is 40px
- **AND** color matrix alpha threshold creates sharp edges
- **AND** merge creates organic, living appearance

---

## How it WORKS (Behavioral)

### Requirement: Rotate animations for arc and circles

The system SHALL animate arc rotation and circle orbiting continuously with linear easing.

#### Scenario: Arc rotation

- **WHEN** progress indicator is visible
- **THEN** arc rotates from 0° → -360° (clockwise direction)
- **AND** rotation duration is 8000ms (8 seconds)
- **AND** easing is linear (no acceleration/deceleration)
- **AND** animation loops infinitely

#### Scenario: Circle orbiting

- **WHEN** progress indicator is visible
- **THEN** each of 9 circles orbits from 0° → 360° (counterclockwise)
- **AND** orbit duration is 8000ms (8 seconds)
- **AND** easing is linear
- **AND** each circle is offset by 40° from previous (360° / 9)
- **AND** animations loop infinitely

#### Scenario: Synchronized animations

- **WHEN** both animations are running
- **THEN** arc and circle animations are synchronized
- **AND** both start simultaneously when indicator appears
- **AND** both complete 8-second cycles simultaneously

### Requirement: Display conditions

The system SHALL only show progress indicator during specific backend processing states.

#### Scenario: Display during backend processing

- **WHEN** backend agent is processing (LangGraph thinking, generating response)
- **THEN** progress indicator appears in center of nucleus
- **AND** indicator appears with fade-in animation (opacity 0 → 1 over 150ms)
- **AND** animations begin immediately

#### Scenario: Display during STT processing

- **WHEN** audio is being sent to speech-to-text service
- **THEN** progress indicator appears in center of voice mode nucleus
- **AND** indicator remains visible until STT completes

#### Scenario: Display during widget generation

- **WHEN** backend is generating or hydrating a widget
- **THEN** progress indicator appears in center of nucleus
- **AND** indicator remains visible until widget emerges

#### Scenario: Hide on backend response

- **WHEN** backend processing completes and response arrives
- **THEN** progress indicator disappears immediately (fade-out 100ms)
- **AND** no collapse or shrink animation (instant disappear)
- **AND** nucleus returns to previous state

#### Scenario: Never show for local UI transitions

- **WHEN** only local UI transitions are occurring (mode morph, cell movement)
- **THEN** progress indicator does NOT appear
- **AND** local animations proceed without progress feedback

### Requirement: Mock processing for library demo

The system SHALL simulate backend processing for library demo purposes.

#### Scenario: Random mock processing triggers

- **WHEN** library demo is running (no real backend)
- **THEN** system triggers mock progress indicator every 8-15 seconds randomly
- **AND** indicator displays for 2-4 seconds randomly
- **AND** this simulates backend processing for visualization

---

## How it's LAYOUT (Positioning)

### Requirement: Center positioning in nucleus

The system SHALL position progress indicator in center of current active nucleus.

#### Scenario: Position in idle nucleus

- **WHEN** backend processing occurs during idle state
- **THEN** progress indicator is centered in idle nucleus
- **AND** indicator overlays nucleus content
- **AND** indicator is positioned absolute at `top: 50%, left: 50%, transform: translate(-50%, -50%)`

#### Scenario: Position in mode nucleus

- **WHEN** backend processing occurs during active mode (voice, chat, etc.)
- **THEN** progress indicator is centered in mode-specific nucleus
- **AND** indicator respects mode nucleus size (may be different from idle)

#### Scenario: Z-index layering

- **WHEN** progress indicator is displayed
- **THEN** indicator has z-index 100 (above nucleus, below modal overlays)
- **AND** indicator does not block interaction with mode islands
- **AND** user can still click/dismiss during progress display
