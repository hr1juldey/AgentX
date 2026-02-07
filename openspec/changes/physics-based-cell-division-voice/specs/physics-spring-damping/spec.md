# Spec: Physics Spring Damping

Spring physics system for smooth cell movement with velocity, acceleration, and damping.

## Purpose

Provide natural momentum-based movement for cells using spring force and velocity damping, creating organic transitions between merged and split states.

---

## How it LOOKS (Visual)

### Requirement: Smooth spring motion

The system SHALL produce visually smooth, organic cell movement with natural easing.

#### Scenario: Cells expand with bounce

- **WHEN** audio starts and energy increases
- **THEN** cells accelerate outward smoothly
- **AND** cells may slightly overshoot target then settle
- **AND** motion feels "bouncy" and organic

#### Scenario: Cells collapse with deceleration

- **WHEN** audio stops and energy decays
- **THEN** cells decelerate smoothly toward nucleus
- **AND** cells don't snap instantly to center
- **AND** motion feels like magnetic attraction

#### Scenario: No jittery movement

- **WHEN** audio level fluctuates rapidly
- **THEN** cell movement remains smooth
- **AND** velocity damping prevents erratic motion
- **AND** visual result is calming, not chaotic

---

## How it WORKS (Behavioral)

### Requirement: Spring force calculation

The system SHALL calculate spring force based on displacement from target distance.

#### Scenario: Spring force proportional to displacement

- **WHEN** cell is at distance 0.3 with target 0.5
- **THEN** spring force = (target - current) * stiffness
- **AND** force pulls cell toward target position

#### Scenario: Higher stiffness = faster response

- **WHEN** spring stiffness is increased to 0.25
- **THEN** cells respond more quickly to energy changes
- **AND** motion feels snappier and more responsive

#### Scenario: Lower stiffness = lazier response

- **WHEN** spring stiffness is decreased to 0.10
- **THEN** cells respond more slowly to energy changes
- **AND** motion feels more relaxed and floaty

---

### Requirement: Velocity accumulation

The system SHALL accumulate velocity from spring force over time for momentum-based movement.

#### Scenario: Velocity builds from spring force

- **WHEN** spring force pulls cell outward
- **THEN** velocity increases in direction of force
- **AND** cell accelerates toward target

#### Scenario: Velocity carries cell past target

- **WHEN** cell reaches target distance with high velocity
- **THEN** cell may overshoot target slightly
- **AND** reverse spring force pulls it back
- **AND** creates natural oscillation before settling

#### Scenario: Zero velocity at equilibrium

- **WHEN** cell reaches target and velocity decays
- **THEN** cell settles at target distance
- **AND** maintains position until energy changes

---

### Requirement: Velocity damping

The system SHALL apply damping factor to velocity each frame to simulate friction/air resistance.

#### Scenario: Velocity decays each frame

- **WHEN** cell has velocity from previous frame
- **THEN** current velocity = previous velocity * damping
- **AND** velocity gradually decreases to zero

#### Scenario: Higher damping = less overshoot

- **WHEN** damping factor is 0.90 (high)
- **THEN** velocity decays quickly
- **AND** cells settle with minimal oscillation

#### Scenario: Lower damping = more bounce

- **WHEN** damping factor is 0.70 (low)
- **THEN** velocity decays slowly
- **AND** cells oscillate longer before settling

---

### Requirement: Position integration

The system SHALL update cell position by adding velocity to current distance.

#### Scenario: Position updates per frame

- **WHEN** animation frame triggers update
- **THEN** new distance = current distance + velocity
- **AND** cell moves incrementally each frame

#### Scenario: Velocity limits prevent explosion

- **WHEN** velocity would cause extreme position change
- **THEN** system clamps velocity to maximum
- **AND** prevents cells from flying off screen

---

## How it INTERACTS (Integration)

### Requirement: Spring physics API

The system SHALL expose function to calculate new position from current state and target.

#### Scenario: Update single cell position

- **WHEN** orbit system requests position update
- **THEN** system accepts: `{ currentDistance, targetDistance, currentVelocity }`
- **AND** returns: `{ newDistance, newVelocity }`
- **AND** internal spring calculation is encapsulated

---

### Requirement: Configuration API

The system SHALL allow configuration of spring stiffness and damping factor.

#### Scenario: Configure spring stiffness

- **WHEN** system initializes with custom stiffness
- **THEN** all spring calculations use configured stiffness
- **AND** stiffness value is stored for future reference

#### Scenario: Configure damping factor

- **WHEN** system initializes with custom damping
- **THEN** all velocity damping uses configured factor
- **AND** damping value is stored for future reference

#### Scenario: Default configuration

- **WHEN** system initializes without custom values
- **THEN** stiffness defaults to 0.15
- **AND** damping defaults to 0.85
- **AND** these values produce natural bouncy motion
