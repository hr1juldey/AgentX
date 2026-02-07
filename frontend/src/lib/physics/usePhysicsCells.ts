/**
 * React hook for physics-based cell animation.
 *
 * Integrates energy accumulator, spring damping, and orbit physics
 * with 60 FPS requestAnimationFrame loop.
 */

'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

import { updateEnergy } from './energy-accumulator';
import { updateCell, OrbitingCell } from './orbit-physics';

/**
 * Physics cells hook return value.
 */
export interface PhysicsCellsState {
  cells: OrbitingCell[];
  energy: number;
  maxDistance: number;
}

/**
 * Physics cells hook API.
 */
export interface PhysicsCellsAPI extends PhysicsCellsState {
  setAudioLevel: (level: number) => void;
  start: () => void;
  stop: () => void;
  isRunning: boolean;
}

/**
 * Configuration for physics cells hook.
 */
export interface PhysicsCellsConfig {
  cellCount?: number;
  baseDistance?: number;
  maxDistance?: number;
  energyGainRate?: number;
  energyDecayRate?: number;
  /** Viscous adhesion - friction when returning to base [0.0, 1.0] */
  viscousAdhesion?: number;
}

/**
 * Default configuration.
 */
const DEFAULT_CONFIG: Required<PhysicsCellsConfig> = {
  cellCount: 8,
  baseDistance: 0.15,
  maxDistance: 0.75,
  energyGainRate: 0.08,
  energyDecayRate: 0.96,
  viscousAdhesion: 0.0,
};

/**
 * Initialize cells with a deterministic seed for SSR.
 * This prevents hydration mismatch while ensuring cells exist on first render.
 */
function initCellsSSR(cellCount: number, baseDistance: number): OrbitingCell[] {
  const colors = ['#00D9FF', '#64FFDA', '#82AAFF', '#FFCB6B', '#FFD700', '#C792EA'];
  return Array.from({ length: cellCount }, (_, i) => {
    const angle = (i / cellCount) * Math.PI * 2;
    // Use a deterministic pattern instead of Math.random()
    const radiusVariation = (i % 3) * 5 + 20;
    const speedVariation = 0.0002 + ((i % 4) * 0.0001);

    return {
      id: `cell-${i}`,
      angle,
      distance: baseDistance,
      velocity: 0,
      speed: 0.002 + speedVariation,
      baseDistance,
      radius: radiusVariation,
      color: colors[i % colors.length],
    };
  });
}

/**
 * React hook for physics-based cell animation.
 *
 * @param config - Physics configuration
 * @returns Physics cells state and control API
 */
export function usePhysicsCells(config: PhysicsCellsConfig = {}): PhysicsCellsAPI {
  // Use a ref to track previous config values for comparison
  const prevConfigRef = useRef<PhysicsCellsConfig | null>(null);

  // Merge config with defaults
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // Debug: log to verify config is received
  console.log(`[usePhysicsCells] Config received - cellCount: ${mergedConfig.cellCount}, baseDistance: ${mergedConfig.baseDistance}`);

  // Initialize with deterministic SSR-safe values (cells always exist)
  const [cells, setCells] = useState<OrbitingCell[]>(() =>
    initCellsSSR(mergedConfig.cellCount, mergedConfig.baseDistance),
  );
  const [energy, setEnergy] = useState(0.0);
  const [isRunning, setIsRunning] = useState(false);

  // Use refs for mutable values in animation loop
  const audioLevelRef = useRef(0.0);
  const energyRef = useRef(0.0);
  const cellsRef = useRef(cells);
  const animationFrameRef = useRef<number | null>(null);
  const configRef = useRef(mergedConfig);
  const lastTimeRef = useRef<number>(performance.now());

  // Keep refs in sync
  cellsRef.current = cells;
  energyRef.current = energy;
  configRef.current = mergedConfig;

  // Re-initialize cells when cellCount or baseDistance changes
  // Use ref-based comparison instead of dependencies to avoid stale closure issues
  useEffect(() => {
    const prevConfig = prevConfigRef.current;
    const shouldReinit =
      !prevConfig ||
      prevConfig.cellCount !== mergedConfig.cellCount ||
      prevConfig.baseDistance !== mergedConfig.baseDistance;

    if (shouldReinit) {
      console.log(`[usePhysicsCells] Re-initializing cells - cellCount: ${mergedConfig.cellCount}, baseDistance: ${mergedConfig.baseDistance}`);
      setCells(initCellsSSR(mergedConfig.cellCount, mergedConfig.baseDistance));
    }

    prevConfigRef.current = mergedConfig;
  });  // Empty dependency array - runs every render but conditionally updates

  /**
   * Set audio level for energy accumulation.
   */
  const setAudioLevel = useCallback((level: number) => {
    audioLevelRef.current = Math.max(0.0, Math.min(1.0, level));
  }, []);

  /**
   * Single animation frame update.
   */
  const tick = useCallback(() => {
    const cfg = configRef.current;
    const currentTime = performance.now();
    const deltaTime = (currentTime - lastTimeRef.current) / 1000; // Convert to seconds
    lastTimeRef.current = currentTime;

    // Update energy from audio level (with delta time for frame-rate independence)
    const newEnergy = updateEnergy(
      energyRef.current,
      audioLevelRef.current,
      {
        gainRate: cfg.energyGainRate,
        decayRate: cfg.energyDecayRate,
      },
      deltaTime,
    );

    // Build spring config with viscous adhesion
    const springConfig = {
      stiffness: 0.15,
      damping: 0.85,
      viscousAdhesion: cfg.viscousAdhesion,
    };

    // Update all cells with spring config
    const newCells = cellsRef.current.map((cell) =>
      updateCell(cell, newEnergy, cfg.maxDistance, springConfig),
    );

    // Update state
    energyRef.current = newEnergy;
    cellsRef.current = newCells;
    setEnergy(newEnergy);
    setCells(newCells);
  }, []);

  /**
   * Start the animation loop.
   */
  const start = useCallback(() => {
    if (isRunning) return;

    setIsRunning(true);
    lastTimeRef.current = performance.now(); // Reset time to avoid huge delta

    const animate = () => {
      tick();
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);
  }, [isRunning, tick]);

  /**
   * Stop the animation loop.
   */
  const stop = useCallback(() => {
    setIsRunning(false);

    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current !== null) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  return {
    cells,
    energy,
    maxDistance: mergedConfig.maxDistance,
    setAudioLevel,
    start,
    stop,
    isRunning,
  };
}
