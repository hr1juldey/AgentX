/**
 * Energy accumulator for audio-reactive physics.
 *
 * Converts audio levels into accumulated energy state with gain and decay.
 * Uses delta time for frame-rate independent physics.
 */

/**
 * Energy accumulator configuration.
 */
export interface EnergyConfig {
  gainRate: number;
  decayRate: number;
}

/**
 * Default energy configuration.
 */
export const DEFAULT_ENERGY_CONFIG: EnergyConfig = {
  gainRate: 0.08,
  decayRate: 0.96,
};

/**
 * Update energy based on audio level.
 *
 * @param currentEnergy - Current energy value [0.0, 1.0]
 * @param audioLevel - Audio level [0.0, 1.0] from analyser
 * @param config - Energy configuration
 * @param deltaTime - Time since last frame in seconds (default: 1/60 for 60fps)
 * @returns New energy value clamped to [0.0, 1.0]
 */
export function updateEnergy(
  currentEnergy: number,
  audioLevel: number,
  config: EnergyConfig = DEFAULT_ENERGY_CONFIG,
  deltaTime: number = 1 / 60,
): number {
  // Accumulate energy from audio (time-scaled)
  let newEnergy = currentEnergy + audioLevel * config.gainRate * deltaTime * 60;

  // Apply decay (energy loss over time, exponential decay)
  // Formula: energy *= decayRate^deltaTime * 60 for frame-rate independence
  newEnergy *= Math.pow(config.decayRate, deltaTime * 60);

  // Clamp to valid range
  return Math.max(0.0, Math.min(1.0, newEnergy));
}
