/**
 * Spring damping physics for Central Island - smooth, organic transitions.
 *
 * Copied from physics-cells-voice and adapted for central-island use.
 * Hooke's Law with damping: F = -kx - cv
 *
 * @see openspec/changes/morphing-central-island/design.md#spring-configuration
 */

/**
 * Spring configuration.
 */
export interface SpringConfig {
  stiffness: number;
  damping: number;
  /** Viscous adhesion - friction when returning to base [0.0, 1.0] */
  viscousAdhesion?: number;
}

/**
 * Default spring configuration.
 */
export const DEFAULT_SPRING_CONFIG: SpringConfig = {
  stiffness: 0.15,
  damping: 0.85,
  viscousAdhesion: 0.0,
};

/**
 * Calculate spring velocity toward target.
 *
 * @param target - Target value
 * @param current - Current value
 * @param velocity - Current velocity
 * @param config - Spring configuration
 * @param maxDistance - Maximum distance for friction scaling (optional)
 * @returns New velocity
 */
export function springDamped(
  target: number,
  current: number,
  velocity: number,
  config: SpringConfig = DEFAULT_SPRING_CONFIG,
  maxDistance?: number,
): number {
  // Spring force: F = k * (target - current)
  const springForce = (target - current) * config.stiffness;

  // Base damping
  let dampingFactor = config.damping;

  // Apply viscous adhesion: extra friction when returning to base
  // Only applies when moving toward target (velocity direction opposite to displacement)
  const displacement = current - target;
  const isReturning = (displacement > 0 && velocity < 0) || (displacement < 0 && velocity > 0);

  if (isReturning && config.viscousAdhesion && maxDistance) {
    // Friction increases as we get closer to base (more "surface contact")
    // Scale by proximity: closer to base = more friction
    const proximityToBase = 1 - Math.abs(displacement) / maxDistance;
    const frictionFactor = config.viscousAdhesion * proximityToBase;

    // Additional damping reduces velocity more strongly when returning
    dampingFactor *= (1 - frictionFactor);

    // Clamp to prevent negative damping (instability)
    dampingFactor = Math.max(0.1, dampingFactor);
  }

  // Apply spring force and damping to velocity
  const newVelocity = (velocity + springForce) * dampingFactor;

  return newVelocity;
}

/**
 * Apply damping factor to velocity.
 *
 * @param velocity - Current velocity
 * @param dampingFactor - Damping factor [0.0, 1.0]
 * @returns Damped velocity
 */
export function applyDamping(velocity: number, dampingFactor: number): number {
  return velocity * dampingFactor;
}
