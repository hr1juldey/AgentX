/**
 * Draggable hook with spring physics.
 *
 * Provides drag functionality for cells with spring lag,
 * z-index management, and shadow effects.
 *
 * @see openspec/changes/morphing-central-island/specs/draggable-cells/draggable-cell-drag-physics
 */

'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

export interface UseDragOptions {
  /** Spring stiffness for drag (default: 600) */
  stiffness?: number;
  /** Spring damping for drag (default: 30) */
  damping?: number;
  /** Drag distance threshold to start drag (default: 5px) */
  dragThreshold?: number;
  /** Callback when drag starts */
  onDragStart?: () => void;
  /** Callback when drag ends */
  onDragEnd?: () => void;
  /** Callback during drag with position */
  onDrag?: (x: number, y: number) => void;
}

export interface UseDragReturn {
  /** Whether currently dragging */
  isDragging: boolean;
  /** Current X position */
  x: number;
  /** Current Y position */
  y: number;
  /** Drag handlers to bind to element */
  dragHandlers: {
    onMouseDown: (e: React.MouseEvent) => void;
    onMouseUp: () => void;
    onMouseLeave: () => void;
    onTouchStart: (e: React.TouchEvent) => void;
    onTouchEnd: () => void;
  };
  /** Reset position to specific coordinates */
  resetPosition: (x: number, y: number) => void;
}

export function useDrag(options: UseDragOptions = {}): UseDragReturn {
  const {
    stiffness = 600,
    damping = 30,
    dragThreshold = 5,
    onDragStart,
    onDragEnd,
    onDrag,
  } = options;

  const [isDragging, setIsDragging] = useState(false);
  const [x, setX] = useState(0);
  const [y, setY] = useState(0);

  const dragStartPos = useRef({ x: 0, y: 0 });
  const currentPos = useRef({ x: 0, y: 0 });
  const isDragActive = useRef(false);
  const animationFrameRef = useRef<number | null>(null);

  // Spring physics update
  const updatePosition = useCallback((targetX: number, targetY: number) => {
    if (animationFrameRef.current !== null) {
      cancelAnimationFrame(animationFrameRef.current);
    }

    const animate = () => {
      // Spring physics: move toward target with stiffness
      const dx = targetX - currentPos.current.x;
      const dy = targetY - currentPos.current.y;

      // Apply spring force
      currentPos.current.x += dx * (stiffness / 10000);
      currentPos.current.y += dy * (stiffness / 10000);

      // Apply damping
      const velocity = Math.sqrt(dx * dx + dy * dy);
      if (velocity < 0.5) {
        // Close enough, snap to target
        currentPos.current.x = targetX;
        currentPos.current.y = targetY;
        setX(targetX);
        setY(targetY);
        onDrag?.(targetX, targetY);
        return;
      }

      setX(currentPos.current.x);
      setY(currentPos.current.y);
      onDrag?.(currentPos.current.x, currentPos.current.y);

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animationFrameRef.current = requestAnimationFrame(animate);
  }, [stiffness, onDrag]);

  // Mouse down handler
  const onMouseDown = useCallback((e: React.MouseEvent) => {
    dragStartPos.current = {
      x: e.clientX,
      y: e.clientY,
    };
    isDragActive.current = false;
  }, []);

  // Touch start handler
  const onTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    dragStartPos.current = {
      x: touch.clientX,
      y: touch.clientY,
    };
    isDragActive.current = false;
  }, []);

  // Mouse move handler (document level)
  const handleMouseMove = useCallback((clientX: number, clientY: number) => {
    const dx = clientX - dragStartPos.current.x;
    const dy = clientY - dragStartPos.current.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Check if drag threshold exceeded
    if (!isDragActive.current && distance > dragThreshold) {
      isDragActive.current = true;
      setIsDragging(true);
      onDragStart?.();
    }

    if (isDragActive.current) {
      updatePosition(clientX, clientY);
    }
  }, [dragThreshold, updatePosition, onDragStart]);

  // Mouse up handler
  const onMouseUp = useCallback(() => {
    if (isDragActive.current) {
      isDragActive.current = false;
      setIsDragging(false);
      onDragEnd?.();
    }
  }, [onDragEnd]);

  const onMouseLeave = useCallback(() => {
    if (isDragActive.current) {
      isDragActive.current = false;
      setIsDragging(false);
      onDragEnd?.();
    }
  }, [onDragEnd]);

  const onTouchEnd = useCallback(() => {
    if (isDragActive.current) {
      isDragActive.current = false;
      setIsDragging(false);
      onDragEnd?.();
    }
  }, [onDragEnd]);

  // Set up document-level mouse move listener
  useEffect(() => {
    const handleDocumentMouseMove = (e: MouseEvent) => {
      handleMouseMove(e.clientX, e.clientY);
    };

    const handleDocumentTouchMove = (e: TouchEvent) => {
      const touch = e.touches[0];
      handleMouseMove(touch.clientX, touch.clientY);
    };

    document.addEventListener('mousemove', handleDocumentMouseMove);
    document.addEventListener('touchmove', handleDocumentTouchMove, { passive: true });

    return () => {
      document.removeEventListener('mousemove', handleDocumentMouseMove);
      document.removeEventListener('touchmove', handleDocumentTouchMove);
    };
  }, [handleMouseMove]);

  const resetPosition = useCallback((newX: number, newY: number) => {
    currentPos.current = { x: newX, y: newY };
    setX(newX);
    setY(newY);
  }, []);

  return {
    isDragging,
    x,
    y,
    dragHandlers: {
      onMouseDown,
      onMouseUp,
      onMouseLeave,
      onTouchStart,
      onTouchEnd,
    },
    resetPosition,
  };
}
