/**
 * Ferrofluid spike physics - models Rosensweig instability.
 *
 * Based on research into ferrofluid speakers where:
 * - Spikes stay tethered to nucleus (surface tension maintains connection)
 * - Energy only gained when connected to nucleus (at base of spike)
 * - Force-based physics (F=ma) instead of spring oscillation
 * - Spikes emerge from nucleus surface, not independent orbits
 *
 * @see https://en.wikipedia.org/wiki/Ferrofluid#Normal-field_instability
 */

/**
 * Ferrofluid cell state - represents a single spike emerging from nucleus.
 */
export interface FerrofluidCell {
  /** Unique identifier */
  id: string;

  /** Angular position around nucleus (radians) */
  angle: number;

  /** Spike height from nucleus surface (0 = at surface, >0 = extended) */
  spikeHeight: number;

  /** Rate of spike height change (positive = growing, negative = shrinking) */
  spikeVelocity: number;

  /** Orbital rotation speed (radians per frame) - gives spinning momentum */
  orbitalSpeed: number;

  /** Mass of the spike (affects acceleration: a = F/m) */
  mass: number;

  /** Magnetic moment - responsiveness to magnetic field */
  magneticMoment: number;

  /** Equilibrium height when no magnetic field (at rest) */
  baseTetherLength: number;

  /** True if spike is connected to nucleus (can gain energy) */
  isConnected: boolean;

  /** Display color of this spike */
  color: string;
}

/**
 * Ferrofluid physics configuration.
 */
export interface FerrofluidConfig {
  /** Number of spikes around nucleus */
  cellCount: number;

  /** Base tether length - spikes start at this height */
  baseTetherLength: number;

  /** Maximum spike extension from nucleus */
  maxSpikeHeight: number;

  /** Magnetic moment - higher = more sensitive to audio (0.0001 to 1.0) */
  magneticMoment: number;

  /** Surface tension - higher = faster return to surface (0.1 to 1.0) */
  surfaceTension: number;

  /** Critical field threshold - audio must exceed this to form spikes (1 to 100) */
  criticalField: number;

  /** Gravitational pull - attraction toward nucleus center (0.1 to 1.0) */
  gravitationalPull: number;
}

/**
 * Default configuration.
 */
export const DEFAULT_FERROFLUID_CONFIG: Required<FerrofluidConfig> = {
  cellCount: 8,
  baseTetherLength: 0.1,
  maxSpikeHeight: 2.0,
  magneticMoment: 0.3,
  surfaceTension: 0.5,
  criticalField: 30,
  gravitationalPull: 0.3,
};

/**
 * Initialize ferrofluid spikes with deterministic seed for SSR.
 */
export function initFerrofluidCells(
  cellCount: number,
  baseTetherLength: number,
): FerrofluidCell[] {
  const colors = ['#00D9FF', '#64FFDA', '#82AAFF', '#FFCB6B', '#FFD700', '#C792EA'];

  return Array.from({ length: cellCount }, (_, i) => {
    const angle = (i / cellCount) * Math.PI * 2;
    const radiusVariation = (i % 3) * 5 + 20;
    const speedVariation = 0.0002 + ((i % 4) * 0.0001);

    return {
      id: `spike-${i}`,
      angle,
      spikeHeight: baseTetherLength,
      spikeVelocity: 0,
      orbitalSpeed: 0.002 + speedVariation,
      mass: 1.0 + (i % 5) * 0.1, // Slight mass variation
      magneticMoment: 1.0,
      baseTetherLength,
      isConnected: true,
      color: colors[i % colors.length],
    };
  });
}

/**
 * Calculate magnetic force from audio level.
 *
 * Magnetic force pushes spike outward, proportional to audio level
 * ABOVE the critical threshold. Only applies when spike is connected.
 *
 * F_mag = magneticMoment × (audioLevel - criticalField) if audio > criticalField
 * F_mag = 0 if spike is not connected
 */
export function magneticForce(
  cell: FerrofluidCell,
  audioLevel: number,
  config: FerrofluidConfig,
): number {
  // No energy gain if not connected to nucleus
  if (!cell.isConnected) {
    return 0;
  }

  // Only form spikes when audio exceeds critical threshold
  const effectiveField = Math.max(0, audioLevel - config.criticalField);

  // Force = magnetic moment × field strength
  return cell.magneticMoment * config.magneticMoment * effectiveField;
}

/**
 * Calculate surface tension force (restoring force).
 *
 * Surface tension acts as a spring tether, pulling spike back
 * toward equilibrium position. This is the "ferrofluid tether"
 * that keeps spikes connected to the main fluid body.
 *
 * F_tension = -k × (height - baseTetherLength)
 */
export function surfaceTensionForce(
  cell: FerrofluidCell,
  config: FerrofluidConfig,
): number {
  const displacement = cell.spikeHeight - cell.baseTetherLength;

  // Hooke's law: F = -k × displacement
  // Negative = restoring force toward nucleus
  return -config.surfaceTension * displacement;
}

/**
 * Calculate gravitational/magnetic pull toward center.
 *
 * Permanent magnet base creates constant attraction toward nucleus.
 * Stronger when spike is further away (simulating field gradient).
 *
 * F_gravity = -g × (1 + spikeHeight)
 */
export function gravitationalForce(
  cell: FerrofluidCell,
  config: FerrofluidConfig,
): number {
  // Always pulls toward nucleus (negative = inward)
  const distanceFactor = 1 + cell.spikeHeight * 0.5;
  return -config.gravitationalPull * distanceFactor;
}

/**
 * Update a single ferrofluid spike using force-based physics.
 *
 * Uses Verlet integration for stability:
 * 1. Sum all forces (magnetic + tension + gravity + damping)
 * 2. Calculate acceleration: a = F / m
 * 3. Update velocity: v = v + a × dt
 * 4. Update position: x = x + v × dt
 *
 * Connection logic: Spike is connected if near base position.
 * Energy can ONLY be gained when connected (at the base).
 */
export function updateFerrofluidCell(
  cell: FerrofluidCell,
  audioLevel: number,
  config: FerrofluidConfig,
  dt: number = 0.016, // ~60 FPS
): FerrofluidCell {
  // Calculate all forces
  const F_mag = magneticForce(cell, audioLevel, config);
  const F_tension = surfaceTensionForce(cell, config);
  const F_gravity = gravitationalForce(cell, config);
  const F_damping = -0.05 * cell.spikeVelocity; // Energy loss

  const netForce = F_mag + F_tension + F_gravity + F_damping;

  // Newton's second law: F = ma → a = F/m
  const acceleration = netForce / cell.mass;

  // Verlet integration
  const newVelocity = cell.spikeVelocity + acceleration * dt;
  const newHeight = cell.spikeHeight + newVelocity * dt;

  // Clamp to valid range
  const clampedHeight = Math.max(
    cell.baseTetherLength,
    Math.min(newHeight, config.maxSpikeHeight),
  );

  // Connection check: spike connected if near base position
  // Energy can only be gained when touching the "ground" (nucleus)
  const connectionThreshold = cell.baseTetherLength * 1.5;
  const isConnected = clampedHeight < connectionThreshold;

  // Orbital rotation (counter-clockwise)
  const newAngle = cell.angle + cell.orbitalSpeed;

  return {
    ...cell,
    angle: newAngle,
    spikeHeight: clampedHeight,
    spikeVelocity: newVelocity,
    isConnected,
  };
}

/**
 * Convert polar coordinates to cartesian position.
 *
 * @returns x, y coordinates and radius for rendering
 */
export function spikeToCartesian(
  cell: FerrofluidCell,
  nucleusRadius: number,
): { x: number; y: number; radius: number } {
  // Spike base position on nucleus surface
  const baseOrbitRadius = nucleusRadius / 2;
  const baseX = Math.cos(cell.angle) * baseOrbitRadius;
  const baseY = Math.sin(cell.angle) * baseOrbitRadius;

  // Spike extends outward from base
  const spikeExtension = cell.spikeHeight * 50; // Scale factor for visibility
  const x = baseX + Math.cos(cell.angle) * spikeExtension;
  const y = baseY + Math.sin(cell.angle) * spikeExtension;

  // Spike radius grows with height (ferrofluid spikes are wider at base)
  const radius = 20 + cell.spikeHeight * 15;

  return { x, y, radius };
}
