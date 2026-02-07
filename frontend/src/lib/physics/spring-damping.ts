/**
 * Spring damping physics for smooth, organic transitions.
 *
 * Hooke's Law with damping: F = -kx - cv
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
 * @returns New velocity
 */
export function springDamped(
  target: number,
  current: number,
  velocity: number,
  config: SpringConfig = DEFAULT_SPRING_CONFIG,
): number {
  // Spring force: F = k * (target - current)
  const springForce = (target - current) * config.stiffness;

  // Apply spring force and damping to velocity
  const newVelocity = (velocity + springForce) * config.damping;

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
