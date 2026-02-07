/**
 * Orbit physics for cell movement around nucleus.
 *
 * Polar coordinates with spring-based distance control.
 */

import { springDamped } from './spring-damping';

/**
 * Single orbiting cell state.
 */
export interface OrbitingCell {
  id: string;
  angle: number;
  distance: number;
  velocity: number;
  speed: number;
  baseDistance: number;
  radius: number;
  color: string;
}

/**
 * Orbit configuration.
 */
export interface OrbitConfig {
  cellCount: number;
  baseDistance: number;
  maxDistance: number;
}

/**
 * Initialize cells distributed around the nucleus.
 *
 * @param count - Number of cells to create
 * @param baseDistance - Base distance from nucleus
 * @returns Array of initialized orbiting cells
 */
export function initializeCells(
  count: number,
  baseDistance: number,
): OrbitingCell[] {
  const colors = [
    '#00D9FF',
    '#64FFDA',
    '#82AAFF',
    '#FFCB6B',
    '#FFD700',
    '#C792EA',
  ];

  return Array.from({ length: count }, (_, i) => {
    const angle = (i / count) * Math.PI * 2;
    return {
      id: `cell-${i}`,
      angle,
      distance: baseDistance,
      velocity: 0,
      speed: 0.002 + Math.random() * 0.001,
      baseDistance,
      radius: 20 + Math.random() * 15,
      color: colors[i % colors.length],
    };
  });
}

/**
 * Update cell state for one frame.
 *
 * @param cell - Cell to update
 * @param energy - Current energy level [0.0, 1.0]
 * @param maxDistance - Maximum orbit distance
 * @param springConfig - Spring configuration for friction
 * @returns Updated cell
 */
export function updateCell(
  cell: OrbitingCell,
  energy: number,
  maxDistance: number,
  springConfig?: import('./spring-damping').SpringConfig,
): OrbitingCell {
  // Target distance expands with energy
  const targetDistance = cell.baseDistance + energy * (maxDistance - cell.baseDistance);

  // Update velocity with spring physics (pass maxDistance for viscous adhesion)
  const newVelocity = springDamped(targetDistance, cell.distance, cell.velocity, springConfig, maxDistance);

  // Apply velocity to distance
  const newDistance = cell.distance + newVelocity;

  // Orbit rotation (counter-clockwise)
  const newAngle = cell.angle + cell.speed;

  return {
    ...cell,
    angle: newAngle,
    distance: newDistance,
    velocity: newVelocity,
  };
}

/**
 * Convert polar coordinates to Cartesian.
 *
 * @param angle - Angle in radians
 * @param distance - Distance from origin
 * @param radius - Cell radius (for centering)
 * @returns { x, y } coordinates
 */
export function polarToCartesian(
  angle: number,
  distance: number,
  radius: number = 0,
): { x: number; y: number } {
  return {
    x: Math.cos(angle) * distance - radius,
    y: Math.sin(angle) * distance - radius,
  };
}
