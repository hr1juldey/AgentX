/**
 * Nucleus physics - energy accumulation and radial emission.
 *
 * The nucleus is the energy source that accumulates voice energy
 * and emits radial force to orbiting cells via inverse square law.
 */

/**
 * Nucleus state configuration.
 */
export interface NucleusConfig {
  baseRadius: number;
  emissionRange: number;
  maxEnergy: number;
}

/**
 * Nucleus state - accumulates energy from voice.
 */
export interface NucleusState {
  energy: number;
  baseRadius: number;
  emissionRange: number;
}

/**
 * Default nucleus configuration.
 */
export const DEFAULT_NUCLEUS_CONFIG: Required<NucleusConfig> = {
  baseRadius: 50,
  emissionRange: 70,
  maxEnergy: 1.0,
};

/**
 * Calculate emission force using inverse square law.
 *
 * Formula: F = energy / (distance² + ε)
 * Where ε prevents division by zero
 *
 * @param nucleusEnergy - Current nucleus energy [0.0, 1.0]
 * @param distance - Distance from nucleus center
 * @param nucleusRadius - Visual radius of nucleus
 * @param intensityMultiplier - Force intensity (default: 5.0)
 * @returns Radial force outward (positive = push away)
 */
export function calculateEmissionForce(
  nucleusEnergy: number,
  distance: number,
  nucleusRadius: number,
  intensityMultiplier: number = 5.0,
): number {
  if (nucleusEnergy < 0.001) return 0;

  // Effective distance from nucleus surface
  const ε = 0.01;
  const effectiveDistance = Math.max(distance - nucleusRadius, ε);

  // Inverse square law
  const rawForce = nucleusEnergy / (effectiveDistance * effectiveDistance);

  return rawForce * intensityMultiplier;
}

/**
 * Update nucleus energy with voice input.
 *
 * Uses same gain/decay pattern as energy-accumulator but for nucleus only.
 *
 * @param currentEnergy - Current nucleus energy
 * @param audioLevel - Voice audio level [0.0, 1.0]
 * @param gainRate - Energy gain rate
 * @param decayRate - Energy decay rate per frame
 * @returns New nucleus energy
 */
export function updateNucleusEnergy(
  currentEnergy: number,
  audioLevel: number,
  gainRate: number = 0.3,
  decayRate: number = 0.98,
): number {
  // Accumulate from voice
  let newEnergy = currentEnergy + audioLevel * gainRate;

  // Decay over time
  newEnergy *= decayRate;

  return Math.max(0.0, Math.min(1.0, newEnergy));
}

/**
 * Check if a cell is within emission range of nucleus.
 *
 * @param cellDistance - Cell distance from nucleus center
 * @param cellRadius - Cell radius
 * @param nucleusEmissionRange - Nucleus emission boundary
 * @returns True if cell can receive emission
 */
export function isInEmissionRange(
  cellDistance: number,
  cellRadius: number,
  nucleusEmissionRange: number,
): boolean {
  const cellOuterEdge = cellDistance + cellRadius;
  return cellOuterEdge <= nucleusEmissionRange;
}

/**
 * Get nucleus visual radius (pulsates with energy).
 *
 * @param baseRadius - Base radius when energy = 0
 * @param energy - Current nucleus energy [0.0, 1.0]
 * @param pulseAmount - How much to grow at max energy (default: 1.3x)
 * @returns Visual radius for rendering
 */
export function getNucleusVisualRadius(
  baseRadius: number,
  energy: number,
  pulseAmount: number = 1.3,
): number {
  return baseRadius * (1 + energy * (pulseAmount - 1));
}
