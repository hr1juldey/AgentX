import { LAYOUT_PHYSICS } from "@/constants/layout-physics";

/**
 * Calculate the repulsive force between two widgets.
 * Uses inverse-square law (like electrostatic force).
 *
 * @param x1 - Widget 1 X position
 * @param y1 - Widget 1 Y position
 * @param w1 - Widget 1 width
 * @param h1 - Widget 1 height
 * @param x2 - Widget 2 X position
 * @param y2 - Widget 2 Y position
 * @param w2 - Widget 2 width
 * @param h2 - Widget 2 height
 * @returns Force vector { fx, fy }
 */
export function calculateRepulsion(
  x1: number,
  y1: number,
  w1: number,
  h1: number,
  x2: number,
  y2: number,
  w2: number,
  h2: number
): { fx: number; fy: number } {
  const dx = x1 - x2;
  const dy = y1 - y2;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Prevent division by zero and limit minimum distance
  const effectiveDistance = Math.max(distance, LAYOUT_PHYSICS.MIN_DISTANCE);

  // Calculate combined size for collision detection
  const minRequiredDist =
    (Math.max(w1, w2) + Math.max(h1, h2)) / 2 + LAYOUT_PHYSICS.WIDGET_PADDING;

  // If widgets overlap, apply stronger repulsion
  const strength =
    distance < minRequiredDist
      ? LAYOUT_PHYSICS.REPULSION_STRENGTH * 3
      : LAYOUT_PHYSICS.REPULSION_STRENGTH;

  // Inverse-square law: F = k / r^2
  const force = strength / (effectiveDistance * effectiveDistance);

  return {
    fx: (dx / distance) * force,
    fy: (dy / distance) * force,
  };
}

/**
 * Calculate the attractive force toward the center of the screen.
 * This keeps widgets from drifting off-screen.
 *
 * @param x - Widget X position
 * @param y - Widget Y position
 * @param centerX - Screen center X coordinate
 * @param centerY - Screen center Y coordinate
 * @returns Force vector { fx, fy }
 */
export function calculateAttraction(
  x: number,
  y: number,
  centerX: number,
  centerY: number
): { fx: number; fy: number } {
  return {
    fx: (centerX - x) * LAYOUT_PHYSICS.ATTRACTION_STRENGTH,
    fy: (centerY - y) * LAYOUT_PHYSICS.ATTRACTION_STRENGTH,
  };
}

/**
 * Apply boundary constraints to keep widgets within viewport.
 *
 * @param x - Widget X position
 * @param y - Widget Y position
 * @param width - Widget width
 * @param height - Widget height
 * @param viewportWidth - Viewport width
 * @param viewportHeight - Viewport height
 * @returns Constrained position { x, y }
 */
export function applyBoundaryConstraints(
  x: number,
  y: number,
  width: number,
  height: number,
  viewportWidth: number,
  viewportHeight: number
): { x: number; y: number } {
  const margin = LAYOUT_PHYSICS.VIEWPORT_MARGIN;
  return {
    x: Math.max(margin, Math.min(viewportWidth - width - margin, x)),
    y: Math.max(margin, Math.min(viewportHeight - height - margin, y)),
  };
}
