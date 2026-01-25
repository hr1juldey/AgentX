import { useCallback } from "react";
import { PanInfo } from "framer-motion";
import { INTERACTION_CONFIG } from "@/constants/widget-constants";
import type { UIDescriptor } from "@/types/widget-types";

interface WidgetHandlersOptions {
  dismissWidget: (id: string) => void;
  setWidgets: React.Dispatch<React.SetStateAction<UIDescriptor[]>>;
  dragStateRef: React.MutableRefObject<Record<string, {
    startPos: { x: number; y: number };
    hasMoved: boolean;
    moveDistance: number;
  }>>;
  handlersCacheRef: React.MutableRefObject<Record<string, unknown>>;
}

interface WidgetHandlers {
  onDismiss: () => void;
  onDragStart: (_: unknown, info: PanInfo) => void;
  onDrag: (_: unknown, info: PanInfo) => void;
  onDragEnd: (_: unknown, info: PanInfo) => void;
  onDragEndCompat: (x: number, y: number) => void;
  onClick: (e: React.MouseEvent) => void;
  onToggleCollapse: () => void;
}

/**
 * Hook for widget interaction handlers
 * Manages widget dismissal, dragging, and collapse toggle
 *
 * @param options - Configuration options and dependencies
 * @returns Object containing widget handler functions
 */
export function useWidgetHandlers(options: WidgetHandlersOptions) {
  const { dismissWidget, setWidgets, dragStateRef, handlersCacheRef } = options;

  /**
   * Toggle widget collapse state
   */
  const toggleWidgetCollapse = useCallback((id: string) => {
    setWidgets((prev) =>
      prev.map((w) =>
        w.descriptor_id === id ? { ...w, collapsed: !w.collapsed } : w
      )
    );
  }, [setWidgets]);

  /**
   * Handle drag end - updates widget position
   * x, y are OFFSETS from the current position (not absolute positions)
   */
  const handleIslandDragEnd = useCallback((id: string, x: number, y: number) => {
    console.log(`🖱️ [DRAG END] ${id} → offset x: ${x.toFixed(1)}, y: ${y.toFixed(1)}`);
    console.trace("Drag end call stack:");

    setWidgets((prev) => {
      const currentWidget = prev.find((w) => w.descriptor_id === id);
      const currentX = currentWidget?.x ?? window.innerWidth / 2;
      const currentY = currentWidget?.y ?? window.innerHeight / 2;
      const newX = currentX + x;
      const newY = currentY + y;

      // Boundary checking - keep widget on screen
      const islandDiameter = 56;
      const padding = 20;
      const boundedX = Math.max(padding, Math.min(window.innerWidth - islandDiameter - padding, newX));
      const boundedY = Math.max(padding, Math.min(window.innerHeight - islandDiameter - padding, newY));

      const updated = prev.map((w) =>
        w.descriptor_id === id ? { ...w, x: boundedX, y: boundedY } : w
      );
      console.log(`🖱️ [DRAG END] Updated widget ${id} x/y in widgets array`);
      return updated;
    });
  }, [setWidgets]);

  /**
   * Get stable handlers for a specific widget
   * Uses cache to prevent re-renders
   *
   * @param id - Widget ID
   * @returns Widget handlers object
   */
  const getWidgetHandlers = useCallback((id: string): WidgetHandlers => {
    // Return cached handlers if available
    if (handlersCacheRef.current[id]) {
      return handlersCacheRef.current[id] as WidgetHandlers;
    }

    // Create new handlers and cache them
    const handleDragStart = (_: unknown, info: PanInfo) => {
      dragStateRef.current[id] = {
        startPos: { x: info.point.x, y: info.point.y },
        hasMoved: false,
        moveDistance: 0,
      };
    };

    const handleDrag = (_: unknown, info: PanInfo) => {
      const state = dragStateRef.current[id];
      if (!state) return;
      const distance = Math.hypot(
        info.point.x - state.startPos.x,
        info.point.y - state.startPos.y
      );
      dragStateRef.current[id] = {
        ...state,
        hasMoved: distance > INTERACTION_CONFIG.CLICK_THRESHOLD,
        moveDistance: distance
      };
    };

    const handleDragEnd = (_: unknown, info: PanInfo) => {
      const state = dragStateRef.current[id];
      const isClick = state && state.moveDistance < INTERACTION_CONFIG.CLICK_THRESHOLD;

      if (!isClick) {
        handleIslandDragEnd(id, info.offset.x, info.offset.y);
      }

      delete dragStateRef.current[id];
    };

    const onDragEndCompat = (x: number, y: number) => {
      const state = dragStateRef.current[id];
      const isClick = state && state.moveDistance < INTERACTION_CONFIG.CLICK_THRESHOLD;

      if (!isClick) {
        handleIslandDragEnd(id, x, y);
      }

      delete dragStateRef.current[id];
    };

    const handlers: WidgetHandlers = {
      onDismiss: () => dismissWidget(id),
      onDragStart: handleDragStart,
      onDrag: handleDrag,
      onDragEnd: handleDragEnd,
      onDragEndCompat,
      onClick: (e: React.MouseEvent) => {
        const state = dragStateRef.current[id];
        const isClick = !state || state.moveDistance < INTERACTION_CONFIG.CLICK_THRESHOLD;
        if (isClick) {
          toggleWidgetCollapse(id);
        }
      },
      onToggleCollapse: () => toggleWidgetCollapse(id),
    };

    // Cache the handlers
    handlersCacheRef.current[id] = handlers;
    return handlers;
    // Note: INTERACTION_CONFIG.CLICK_THRESHOLD is a constant, so we exclude it from deps
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dismissWidget, handleIslandDragEnd, toggleWidgetCollapse]);

  return {
    toggleWidgetCollapse,
    handleIslandDragEnd,
    getWidgetHandlers,
  };
}
