/**
 * Contact detection for nucleus-cell boundary interaction.
 *
 * Determines when cells are within range to receive
 * radial energy emission from the nucleus.
 */

/**
 * Contact detection configuration.
 */
export interface ContactConfig {
  nucleusRadius: number;
  cellRadius: number;
  threshold: number;  // Multiplier for emission boundary
}

/**
 * Default contact configuration.
 */
export const DEFAULT_CONTACT_CONFIG: Required<ContactConfig> = {
  nucleusRadius: 50,
  cellRadius: 25,
  threshold: 1.4,  // 140% of combined radii = emission range
};

/**
 * Detect if cell is in contact with nucleus emission field.
 *
 * A cell is "in contact" when its outer edge is within
 * the emission range of the nucleus.
 *
 * @param cellDistance - Distance from nucleus center to cell center
 * @param nucleusRadius - Radius of nucleus
 * @param cellRadius - Radius of orbiting cell
 * @param threshold - Emission range multiplier (default: 1.4)
 * @returns True if cell can receive emission
 */
export function detectContact(
  cellDistance: number,
  nucleusRadius: number,
  cellRadius: number,
  threshold: number = 1.4,
): boolean {
  // Combined radius of both bodies
  const combinedRadius = nucleusRadius + cellRadius;

  // Emission boundary (slightly larger than physical contact)
  const emissionBoundary = combinedRadius * threshold;

  // Cell is in contact if its center is within emission boundary
  return cellDistance <= emissionBoundary;
}

/**
 * Calculate contact strength (0.0 to 1.0).
 *
 * Stronger when closer to nucleus center, following
 * inverse relationship with distance.
 *
 * @param cellDistance - Distance from nucleus center
 * @param nucleusRadius - Radius of nucleus
 * @param cellRadius - Radius of orbiting cell
 * @param threshold - Emission range multiplier
 * @returns Contact strength [0.0, 1.0]
 */
export function getContactStrength(
  cellDistance: number,
  nucleusRadius: number,
  cellRadius: number,
  threshold: number = 1.4,
): number {
  const combinedRadius = nucleusRadius + cellRadius;
  const emissionBoundary = combinedRadius * threshold;

  if (cellDistance >= emissionBoundary) return 0;
  if (cellDistance <= nucleusRadius) return 1;

  // Linear falloff from center to boundary
  const range = emissionBoundary - nucleusRadius;
  const distanceIntoRange = cellDistance - nucleusRadius;
  return 1 - (distanceIntoRange / range);
}

/**
 * Get emission boundary radius for visualization.
 *
 * @param nucleusRadius - Radius of nucleus
 * @param cellRadius - Radius of orbiting cell (for reference)
 * @param threshold - Emission range multiplier
 * @returns Boundary radius in same units as input
 */
export function getEmissionBoundary(
  nucleusRadius: number,
  cellRadius: number = 25,
  threshold: number = 1.4,
): number {
  return (nucleusRadius + cellRadius) * threshold;
}
