/**
 * Physics constants for nucleus-driven cell animation.
 *
 * All magic numbers centralized for easier tuning and management.
 */

// ============================================================================
// EMISSION PHYSICS CONSTANTS
// ============================================================================

/**
 * Epsilon for preventing division by zero in inverse square law.
 * Small value that avoids mathematical singularities.
 */
export const EPSILON = 0.01;

/**
 * Base intensity multiplier for emission force.
 * Higher values = stronger push from nucleus to cells.
 */
export const DEFAULT_EMISSION_INTENSITY = 5.0;

/**
 * Emission range threshold (multiplier of combined radii).
 * Cells within this distance can receive emission force.
 * 1.4 = 140% of (nucleusRadius + cellRadius)
 */
export const DEFAULT_EMISSION_THRESHOLD = 1.4;

/**
 * Minimum energy level for emission to occur.
 * Nucleus energy below this value won't push cells.
 */
export const EMISSION_ENERGY_THRESHOLD = 0.01;

/**
 * Minimum energy for emission visualization (glow).
 */
export const EMISSION_VISUAL_THRESHOLD = 0.05;

// ============================================================================
// NUCLEUS VISUAL CONSTANTS
// ============================================================================

/**
 * Pulse amount for nucleus radius at max energy.
 * 1.3 = 30% larger when energy = 1.0
 */
export const NUCLEUS_PULSE_AMOUNT = 1.3;

/**
 * Energy threshold for nucleus color change (inactive → active).
 */
export const NUCLEUS_ACTIVE_THRESHOLD = 0.3;

/**
 * Average cell radius (used for emission boundary calculation).
 * All cells vary slightly around this base value.
 */
export const AVG_CELL_RADIUS = 25;

// ============================================================================
// SPRING PHYSICS CONSTANTS
// ============================================================================

/**
 * Spring stiffness coefficient (Hooke's Law: F = -kx).
 * Higher values = stronger pull back to base distance.
 */
export const SPRING_STIFFNESS = 0.15;

/**
 * Base damping factor (velocity decay per frame).
 * Lower values = more damping (slower movement).
 */
export const SPRING_DAMPING = 0.85;

/**
 * Minimum damping factor (safety clamp).
 * Prevents negative damping which would cause instability.
 */
export const MIN_DAMPING_FACTOR = 0.1;

// ============================================================================
// MOTION INTEGRATION CONSTANTS
// ============================================================================

/**
 * Time step factor for force application.
 * Scales the effect of forces on velocity.
 * Lower values = smoother but slower response.
 */
export const TIME_STEP_FACTOR = 0.1;

// ============================================================================
// DISTANCE CLAMPING CONSTANTS
// ============================================================================

/**
 * Minimum distance multiplier (can't go inside nucleus).
 * Cells are pushed out if they get too close.
 */
export const MIN_DISTANCE_MULTIPLIER = 0.5;

/**
 * Maximum distance multiplier (soft upper bound).
 * Cells can briefly exceed this during strong emission.
 */
export const MAX_DISTANCE_MULTIPLIER = 2.0;

/**
 * ViewBox size multiplier for rendering.
 * Allocates space for cells pushed outward by emission.
 */
export const VIEWBOX_MULTIPLIER = 2.5;

// ============================================================================
// VISUALIZATION CONSTANTS
// ============================================================================

/**
 * Cell opacity increase when receiving emission.
 */
export const EMISSION_RECEIVE_OPACITY = 1.0;

/**
 * Default cell opacity when not receiving emission.
 */
export const DEFAULT_CELL_OPACITY = 0.85;

/**
 * Brightness filter multiplier for cells receiving emission.
 * brightness(1 + X) where X = this value * nucleusEnergy
 */
export const EMISSION_BRIGHTNESS_MULTIPLIER = 0.5;

/**
 * Emission glow animation duration (seconds).
 * Scales with energy: higher energy = faster pulse.
 */
export const EMISSION_PULSE_DURATION_BASE = 2.0;

// ============================================================================
// CELL INITIALIZATION CONSTANTS
// ============================================================================

/**
 * Tangential orbit speed (radians per frame).
 * Controls how fast cells orbit around nucleus.
 */
export const BASE_ORBIT_SPEED = 0.002;

/**
 * Random orbit speed variation range.
 */
export const ORBIT_SPEED_VARIATION = 0.001;

/**
 * Base cell radius (pixels).
 */
export const BASE_CELL_RADIUS = 20;

/**
 * Cell radius variation range (pixels).
 */
export const CELL_RADIUS_VARIATION = 15;

/**
 * Cell initialization pattern modulus.
 * Used for deterministic variation across cells.
 */
export const CELL_PATTERN_MODULUS = 3;
