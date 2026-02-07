/**
 * React hook for ferrofluid spike animation.
 *
 * Models Rosensweig instability with force-based physics (F=ma).
 * Spikes stay tethered to nucleus and only gain energy when connected.
 *
 * @see agentx/frontend/src/lib/physics/ferrofluid-physics.ts
 */

'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

import {
  FerrofluidCell,
  FerrofluidConfig,
  DEFAULT_FERROFLUID_CONFIG,
  initFerrofluidCells,
  updateFerrofluidCell,
  spikeToCartesian,
} from './ferrofluid-physics';

/**
 * Ferrofluid cells hook return value.
 */
export interface FerrofluidCellsState {
  cells: FerrofluidCell[];
  maxSpikeHeight: number;
}

/**
 * Ferrofluid cells hook API.
 */
export interface FerrofluidCellsAPI extends FerrofluidCellsState {
  setAudioLevel: (level: number) => void;
  start: () => void;
  stop: () => void;
  isRunning: boolean;
}

/**
 * Configuration for ferrofluid cells hook.
 */
export interface FerrofluidCellsConfig {
  cellCount?: number;
  baseTetherLength?: number;
  maxSpikeHeight?: number;
  magneticMoment?: number;
  surfaceTension?: number;
  criticalField?: number;
  gravitationalPull?: number;
}

/**
 * Default configuration.
 */
const DEFAULT_CONFIG: Required<FerrofluidCellsConfig> = {
  cellCount: 8,
  baseTetherLength: 0.1,
  maxSpikeHeight: 2.0,
  magneticMoment: 0.3,
  surfaceTension: 0.5,
  criticalField: 30,
  gravitationalPull: 0.3,
};

/**
 * React hook for ferrofluid spike animation.
 *
 * @param config - Ferrofluid physics configuration
 * @returns Ferrofluid cells state and control API
 */
export function useFerrofluidCells(config: FerrofluidCellsConfig = {}): FerrofluidCellsAPI {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };

  // Initialize with deterministic SSR-safe values (cells always exist)
  const [cells, setCells] = useState<FerrofluidCell[]>(() =>
    initFerrofluidCells(mergedConfig.cellCount, mergedConfig.baseTetherLength),
  );
  const [isRunning, setIsRunning] = useState(false);

  // Use refs for mutable values in animation loop
  const audioLevelRef = useRef(0.0);
  const cellsRef = useRef(cells);
  const animationFrameRef = useRef<number | null>(null);
  const configRef = useRef(mergedConfig);

  // Keep refs in sync
  cellsRef.current = cells;
  configRef.current = mergedConfig;

  /**
   * Set audio level for spike animation.
   */
  const setAudioLevel = useCallback((level: number) => {
    audioLevelRef.current = Math.max(0.0, Math.min(1.0, level));
  }, []);

  /**
   * Single animation frame update.
   */
  const tick = useCallback(() => {
    const cfg = configRef.current;
    const audioLevel = audioLevelRef.current;

    // Normalize audio to 0-100 range for physics calculations
    const normalizedAudio = audioLevel * 100;

    // Update all cells using ferrofluid physics
    const newCells = cellsRef.current.map((cell) =>
      updateFerrofluidCell(cell, normalizedAudio, cfg),
    );

    // Update state
    cellsRef.current = newCells;
    setCells(newCells);
  }, []);

  /**
   * Start the animation loop.
   */
  const start = useCallback(() => {
    if (isRunning) return;

    setIsRunning(true);

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
    maxSpikeHeight: mergedConfig.maxSpikeHeight,
    setAudioLevel,
    start,
    stop,
    isRunning,
  };
}

/**
 * Export the spike to cartesian conversion for component rendering.
 */
export { spikeToCartesian };
