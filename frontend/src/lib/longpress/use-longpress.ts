/**
 * Longpress detection hook for Central Island.
 *
 * Detects 1.5s longpress with haptic feedback at 1.0s.
 * Supports cancel on move away (> 50px) or click free space.
 *
 * @see openspec/changes/morphing-central-island/specs/nucleus-longpress-trigger
 */

'use client';

import { useEffect, useRef, useState, useCallback } from 'react';

export interface UseLongpressOptions {
  /** Longpress duration in milliseconds (default: 1500) */
  duration?: number;
  /** Haptic feedback time in milliseconds (default: 1000) */
  hapticTime?: number;
  /** Cancel threshold - move away > this distance cancels (default: 50px) */
  cancelThreshold?: number;
  /** Callback when longpress completes */
  onLongpress?: () => void;
  /** Callback when longpress is cancelled */
  onCancel?: () => void;
  /** Callback when haptic feedback should trigger */
  onHaptic?: () => void;
}

export interface UseLongpressReturn {
  /** Whether longpress is currently active (completed) */
  isLongpressActive: boolean;
  /** Progress from 0 to 1 during longpress */
  longpressProgress: number;
  /** Bind these props to your target element */
  bind: {
    onMouseDown: (e: React.MouseEvent) => void;
    onMouseUp: () => void;
    onMouseLeave: () => void;
    onTouchStart: (e: React.TouchEvent) => void;
    onTouchEnd: () => void;
  };
}

/**
 * Hook for detecting longpress gestures with haptic feedback.
 *
 * Features:
 * - Configurable duration (default 1500ms)
 * - Haptic feedback at 1.0s (navigator.vibrate)
 * - Cancel on move away > 50px
 * - Progress tracking (0-1)
 * - Mouse and touch support
 *
 * @example
 * ```tsx
 * const { isLongpressActive, longpressProgress, bind } = useLongpress({
 *   duration: 1500,
 *   onLongpress: () => console.log('Longpress triggered!'),
 * });
 *
 * <button {...bind}>Hold me</button>
 * ```
 */
export function useLongpress(options: UseLongpressOptions = {}): UseLongpressReturn {
  const {
    duration = 1500,
    hapticTime = 1000,
    cancelThreshold = 50,
    onLongpress,
    onCancel,
    onHaptic,
  } = options;

  const [isLongpressActive, setIsLongpressActive] = useState(false);
  const [longpressProgress, setLongpressProgress] = useState(0);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const hapticTriggeredRef = useRef(false);
  const startPositionRef = useRef<{ x: number; y: number } | null>(null);
  const isPressedRef = useRef(false);

  // Reset state
  const reset = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    setLongpressProgress(0);
    hapticTriggeredRef.current = false;
    startPositionRef.current = null;
    isPressedRef.current = false;
  }, []);

  // Cancel longpress
  const cancel = useCallback(() => {
    console.log('[useLongpress] Cancel called, isPressed:', isPressedRef.current);
    if (isPressedRef.current) {
      onCancel?.();
    }
    reset();
  }, [onCancel, reset]);

  // Complete longpress
  const complete = useCallback(() => {
    setIsLongpressActive(true);
    setLongpressProgress(1);
    isPressedRef.current = false;
    onLongpress?.();
  }, [onLongpress]);

  // Start longpress timer
  const start = useCallback((clientX: number, clientY: number) => {
    console.log('[useLongpress] Starting longpress at', { x: clientX, y: clientY });
    reset();
    isPressedRef.current = true;
    startPositionRef.current = { x: clientX, y: clientY };
    hapticTriggeredRef.current = false;

    const startTime = Date.now();

    // Update progress every 16ms (~60fps)
    const progressInterval = setInterval(() => {
      if (!isPressedRef.current) {
        console.log('[useLongpress] Press released, clearing interval');
        clearInterval(progressInterval);
        return;
      }

      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      setLongpressProgress(progress);

      // Debug: log progress every 500ms
      if (elapsed % 500 < 20) {
        console.log(`[useLongpress] Progress: ${(progress * 100).toFixed(0)}%`);
      }

      // Haptic feedback at hapticTime
      if (progress >= hapticTime / duration && !hapticTriggeredRef.current) {
        console.log('[useLongpress] Haptic feedback triggered');
        hapticTriggeredRef.current = true;
        onHaptic?.();
        // Trigger haptic vibration on mobile
        if (typeof navigator !== 'undefined' && 'vibrate' in navigator) {
          navigator.vibrate(200);
        }
      }

      // Complete longpress
      if (progress >= 1) {
        console.log('[useLongpress] Complete! Triggering onLongpress callback');
        clearInterval(progressInterval);
        complete();
      }
    }, 16);

    timerRef.current = setTimeout(() => {
      clearInterval(progressInterval);
      if (isPressedRef.current) {
        console.log('[useLongpress] Timer complete, triggering longpress');
        complete();
      }
    }, duration);
  }, [duration, hapticTime, complete, onHaptic, reset]);

  // Check if moved too far (cancel longpress)
  const checkCancel = useCallback((clientX: number, clientY: number) => {
    if (!startPositionRef.current || !isPressedRef.current) return false;

    const dx = clientX - startPositionRef.current.x;
    const dy = clientY - startPositionRef.current.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > cancelThreshold) {
      cancel();
      return true;
    }
    return false;
  }, [cancelThreshold, cancel]);

  // Mouse handlers
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    console.log('[useLongpress] onMouseDown triggered');
    start(e.clientX, e.clientY);
  }, [start]);

  const onMouseUp = useCallback(() => {
    console.log('[useLongpress] onMouseUp triggered, isLongpressActive:', isLongpressActive);
    if (!isLongpressActive && isPressedRef.current) {
      cancel();
    }
  }, [isLongpressActive, cancel]);

  const onMouseLeave = useCallback(() => {
    console.log('[useLongpress] onMouseLeave triggered');
    if (isPressedRef.current) {
      cancel();
    }
  }, [cancel]);

  const onMouseMove = useCallback((e: React.MouseEvent) => {
    checkCancel(e.clientX, e.clientY);
  }, [checkCancel]);

  // Touch handlers
  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    console.log('[useLongpress] onTouchStart triggered');
    start(touch.clientX, touch.clientY);
  }, [start]);

  const onTouchEnd = useCallback(() => {
    console.log('[useLongpress] onTouchEnd triggered, isLongpressActive:', isLongpressActive);
    if (!isLongpressActive && isPressedRef.current) {
      cancel();
    }
  }, [isLongpressActive, cancel]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      reset();
    };
  }, [reset]);

  return {
    isLongpressActive,
    longpressProgress,
    bind: {
      onMouseDown,
      onMouseUp,
      onMouseLeave,
      onTouchStart,
      onTouchEnd,
      // @ts-ignore - adding onMouseMove for internal use
      onMouseMove,
    },
  };
}
