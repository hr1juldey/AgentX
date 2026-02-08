/**
 * Physics renderer component for Central Island.
 *
 * Copied from physics-cells-voice and adapted for central-island use.
 * Provides 60 FPS requestAnimationFrame loop for smooth animations.
 *
 * @see openspec/changes/morphing-central-island/specs/audio-reactive-rendering
 */

'use client';

import { useEffect, useRef, useCallback, useState } from 'react';

export interface PhysicsRendererState {
  isRunning: boolean;
  frameCount: number;
}

export interface PhysicsRendererConfig {
  /** Target FPS (default: 60) */
  targetFPS?: number;
  /** Enable debug logging */
  debug?: boolean;
}

export interface PhysicsRendererAPI extends PhysicsRendererState {
  start: () => void;
  stop: () => void;
  /** Register a callback to be called each frame */
  onFrame: (callback: (deltaTime: number) => void) => () => void;
}

const DEFAULT_CONFIG: Required<PhysicsRendererConfig> = {
  targetFPS: 60,
  debug: false,
};

/**
 * Physics renderer hook for 60 FPS animation loop.
 *
 * Provides frame-accurate timing for smooth physics animations.
 * Adapted from physics-cells-voice for widget cell spawning (instead of audio).
 *
 * @param config - Renderer configuration
 * @returns Physics renderer API
 */
export function usePhysicsRenderer(config: PhysicsRendererConfig = {}): PhysicsRendererAPI {
  const mergedConfig = { ...DEFAULT_CONFIG, ...config };
  const [isRunning, setIsRunning] = useState(false);
  const [frameCount, setFrameCount] = useState(0);

  const animationFrameRef = useRef<number | null>(null);
  const lastTimeRef = useRef<number>(performance.now());
  const frameCallbacksRef = useRef<Set<(deltaTime: number) => void>>(new Set());

  /**
   * Register a frame callback.
   * Returns cleanup function to unregister.
   */
  const onFrame = useCallback((callback: (deltaTime: number) => void) => {
    frameCallbacksRef.current.add(callback);

    // Return cleanup function
    return () => {
      frameCallbacksRef.current.delete(callback);
    };
  }, []);

  /**
   * Single animation frame update.
   */
  const tick = useCallback(() => {
    const currentTime = performance.now();
    const deltaTime = (currentTime - lastTimeRef.current) / 1000; // Convert to seconds
    lastTimeRef.current = currentTime;

    // Call all registered frame callbacks
    frameCallbacksRef.current.forEach((callback) => {
      callback(deltaTime);
    });

    setFrameCount((prev) => prev + 1);

    // Debug logging
    if (mergedConfig.debug && Math.random() < 0.01) {
      console.log(`[PhysicsRenderer] Frame ${frameCount}, Delta: ${deltaTime.toFixed(3)}s`);
    }
  }, [frameCount, mergedConfig.debug]);

  /**
   * Start the animation loop.
   */
  const start = useCallback(() => {
    if (isRunning) return;

    setIsRunning(true);
    lastTimeRef.current = performance.now();

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
    isRunning,
    frameCount,
    start,
    stop,
    onFrame,
  };
}
