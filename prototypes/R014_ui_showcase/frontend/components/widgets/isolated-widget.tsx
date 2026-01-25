"use client";

import { memo, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence, PanInfo } from "framer-motion";
import { X, Minimize2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ToolIsland } from "@/components/islands/tool-island";
import { DirectWidgetRenderer } from "@/components/widgets/direct-widget-renderer";
import { useWidgetStore, type UIDescriptor, type ViewState, type Position } from "@/store/widget-store";

// Constants
const NOOP_FN = () => {};
const NOOP_DRAG_FN = (_x: number, _y: number) => {};
const STOP_PROPAGATION = (e: React.MouseEvent) => e.stopPropagation();

interface IsolatedWidgetProps {
  descriptorId: string;
}

/**
 * IsolatedWidget - A self-contained widget component using Zustand for state management.
 *
 * KEY DESIGN PRINCIPLE (Jira/Linear style isolation):
 * - Uses plain objects in Zustand store (not Maps) for granular change tracking
 * - Selector (s) => s.widgets[descriptorId] ONLY triggers re-render when THIS widget changes
 * - When other widgets are added/deleted, THIS widget's selector returns the same reference
 * - Zustand's shallow equality check (Object.is) sees the reference hasn't changed
 * - Result: NO re-render for unrelated widget changes
 *
 * This is how production card-based UIs handle hundreds of items efficiently:
 * - Jira tickets: Each ticket component subscribes to its own ticket data
 * - Linear issues: Each issue subscribes to its own issue data
 * - Asana tasks: Each task subscribes to its own task data
 *
 * The secret: Plain objects + property access = isolated subscriptions
 * Maps DON'T work because Zustand can't track which key you accessed
 */
export const IsolatedWidget = memo(function IsolatedWidget({
  descriptorId,
}: IsolatedWidgetProps) {
  // CRITICAL: These selectors create isolated subscriptions
  // They ONLY re-render when the specific value for descriptorId changes
  // When other widgets are added/deleted, these specific values don't change
  // So Zustand's shallow equality (Object.is) returns true → no re-render
  const widget = useWidgetStore((s) => s.widgets[descriptorId]);
  const viewState = useWidgetStore((s) => s.viewStates[descriptorId]) as ViewState | undefined;
  const position = useWidgetStore((s) => s.positions[descriptorId]);

  // Actions from store - stable references, never recreated
  const cycleState = useWidgetStore((s) => s.cycleViewState);
  const updatePositionDelta = useWidgetStore((s) => s.updatePositionDelta);
  const removeWidget = useWidgetStore((s) => s.removeWidget);

  // Early return if widget doesn't exist (was deleted from store)
  if (!widget || !viewState || !position) {
    return null;
  }

  /**
   * Cycle handler - calls store action
   */
  const handleCycleState = useCallback(() => {
    cycleState(descriptorId);
  }, [cycleState, descriptorId]);

  /**
   * Drag end handler - updates position via store
   */
  const handleDragEnd = useCallback(
    (x: number, y: number) => {
      updatePositionDelta(descriptorId, x, y);
    },
    [updatePositionDelta, descriptorId]
  );

  /**
   * Dismiss handler - removes widget from store
   */
  const handleDismiss = useCallback(() => {
    removeWidget(descriptorId);
  }, [removeWidget, descriptorId]);

  // Track drag distance to distinguish clicks from drags
  const dragDistanceRef = useRef(0);
  const CLICK_THRESHOLD = 5;

  const handleDrag = useCallback(() => {
    dragDistanceRef.current++;
  }, []);

  const handleClick = useCallback(() => {
    // Only cycle if it was a click (not a drag)
    if (dragDistanceRef.current < CLICK_THRESHOLD) {
      handleCycleState();
    }
    dragDistanceRef.current = 0;
  }, [handleCycleState]);

  // Island state uses ToolIsland's own drag detection
  const handleIslandDragEnd = useCallback((x: number, y: number) => {
    updatePositionDelta(descriptorId, x, y);
  }, [updatePositionDelta, descriptorId]);

  // Card/Full states use local drag detection
  const handleDragEndWrapper = useCallback(
    (_: unknown, info: PanInfo) => {
      handleDragEnd(info.offset.x, info.offset.y);
    },
    [handleDragEnd]
  );

  const handleDismissClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    handleDismiss();
  }, [handleDismiss]);

  // Debug logging for render verification (can be removed in production)
  useEffect(() => {
    console.log(`[IsolatedWidget ${descriptorId}] Rendered, viewState:`, viewState);
  }, [descriptorId, viewState]);

  // Get widget icon based on type
  const getWidgetIcon = () => {
    switch (widget.descriptor_type) {
      case "markdown":
        return "📝";
      case "card":
        return "📇";
      case "form":
        return "📋";
      case "progress":
        return "📊";
      case "action":
        return "⚡";
      case "confirmation":
        return "❓";
      case "image":
        return "🖼️";
      case "gallery":
        return "🖼️";
      case "chart":
        return "📈";
      case "search-result":
        return "🔍";
      case "hop-progress":
        return "🔄";
      case "citation-card":
        return "📚";
      default:
        return "📦";
    }
  };

  // Get color for widget type
  const getWidgetColor = () => {
    const colors: Record<string, string> = {
      markdown: "hsl(var(--island-markdown))",
      card: "hsl(var(--island-card))",
      form: "hsl(var(--island-form))",
      progress: "hsl(var(--island-progress))",
      action: "hsl(var(--island-action))",
      confirmation: "hsl(var(--island-confirmation))",
      image: "hsl(var(--island-image))",
      gallery: "hsl(var(--island-gallery))",
      chart: "hsl(var(--island-chart))",
      "search-result": "hsl(var(--island-search-result))",
      "hop-progress": "hsl(var(--island-hop-progress))",
      "citation-card": "hsl(var(--island-citation-card))",
    };
    return colors[widget.descriptor_type] || "hsl(var(--island-white))";
  };

  const widgetColor = getWidgetColor();
  const currentState = viewState;
  const zIndex = 1000;

  return (
    <AnimatePresence mode="wait">
      {viewState === "island" && (
        <ToolIsland
          key="island"
          widget={widget}
          position={position}
          isActive={false}
          onClick={handleCycleState}
          onDragEnd={handleIslandDragEnd}
        />
      )}

      {viewState === "card" && (
        <motion.div
          key="card"
          drag
          dragElastic={0}
          dragMomentum={false}
          whileDrag={{ cursor: "grabbing", scale: 1.02 }}
          onDrag={handleDrag}
          onDragEnd={handleDragEndWrapper}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.22 }}
          className="fixed pointer-events-auto"
          style={{ x: position.x, y: position.y, position: "fixed", zIndex }}
        >
          <motion.div
            className="relative group cursor-pointer select-text"
            onClick={handleClick}
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            {/* Card container */}
            <motion.div
              className="rounded-2xl shadow-2xl backdrop-blur-md bg-card/95 border border-border/50 overflow-hidden"
              style={{ width: 320 }}
              whileHover={{ boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.4)" }}
            >
              {/* Header with icon, title, and cycle indicator */}
              <div
                className="flex items-center gap-3 p-4 border-b border-border/50"
                style={{ background: widgetColor }}
              >
                <span className="text-2xl">{getWidgetIcon()}</span>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-sm text-white truncate select-text">
                    {widget.title || widget.descriptor_type}
                  </h3>
                </div>
                {/* Cycle indicator */}
                <div className="flex gap-1">
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${
                      currentState === "island" ? "bg-white" : "bg-white/30"
                    }`}
                  />
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${
                      currentState === "card" ? "bg-white" : "bg-white/30"
                    }`}
                  />
                  <div
                    className={`w-1.5 h-1.5 rounded-full ${
                      currentState === "full" ? "bg-white" : "bg-white/30"
                    }`}
                  />
                </div>
              </div>

              {/* Content summary with markdown rendering */}
              <div className="p-4 overflow-hidden">
                <div className="text-sm text-foreground/80 line-clamp-3 select-text prose prose-sm max-w-none dark:prose-invert [&>*]:mb-0 [&>*]:mt-0 [&_p]:inline [&_ul]:inline [&_ol]:inline [&_li]:inline">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {widget.content || "Click to expand"}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Footer with hint */}
              <div className="px-4 py-2 bg-muted/50 border-t border-border/50">
                <p className="text-xs text-muted-foreground text-center">
                  Click to expand • Drag to move
                </p>
              </div>
            </motion.div>

            {/* Dismiss button */}
            <button
              onClick={handleDismissClick}
              className="absolute -top-2 -right-2 p-1.5 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity shadow-lg"
              aria-label="Dismiss widget"
            >
              <X className="w-3 h-3" />
            </button>
          </motion.div>
        </motion.div>
      )}

      {viewState === "full" && (
        <motion.div
          key="full"
          drag
          dragElastic={0}
          dragMomentum={false}
          whileDrag={{ cursor: "grabbing" }}
          onDrag={handleDrag}
          onDragEnd={handleDragEndWrapper}
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          transition={{ duration: 0.22 }}
          className="fixed pointer-events-auto"
          style={{ x: position.x, y: position.y, position: "fixed", zIndex }}
        >
          <div className="relative group">
            {/* Integrated header with cycle button */}
            <motion.div
              className="flex items-center gap-3 px-4 py-3 rounded-t-2xl border-b border-border/50 select-text"
              style={{ background: widgetColor }}
              onClick={handleClick}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.99 }}
            >
              <span className="text-2xl">{getWidgetIcon()}</span>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-base text-white truncate select-text">
                  {widget.title || widget.descriptor_type}
                </h3>
              </div>
              {/* Cycle indicator */}
              <div className="flex gap-1 mr-2">
                <div
                  className={`w-1.5 h-1.5 rounded-full ${
                    currentState === "island" ? "bg-white" : "bg-white/30"
                  }`}
                />
                <div
                  className={`w-1.5 h-1.5 rounded-full ${
                    currentState === "card" ? "bg-white" : "bg-white/30"
                  }`}
                />
                <div
                  className={`w-1.5 h-1.5 rounded-full ${
                    currentState === "full" ? "bg-white" : "bg-white/30"
                  }`}
                />
              </div>
              {/* Integrated cycle button (Minimize2 icon) */}
              <Minimize2 className="w-4 h-4 text-white/70" />
            </motion.div>

            {/* Content - pass no-op dismiss to prevent accidental deletion */}
            <div
              className="rounded-b-2xl shadow-2xl backdrop-blur-md bg-card/95 border border-t-0 border-border/50 overflow-hidden select-text"
              onClick={STOP_PROPAGATION}
            >
              <DirectWidgetRenderer
                descriptor={widget as any}
                onDismiss={NOOP_FN}
                dragPosition={{ x: 0, y: 0 }}
                onDragEnd={NOOP_DRAG_FN}
                disableDrag={true} // Disable inner widget drag - only outer container draggable
              />
            </div>

            {/* Dismiss button */}
            <button
              onClick={handleDismissClick}
              className="absolute top-16 right-2 p-2 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 hover:opacity-100 transition-opacity shadow-lg"
              aria-label="Dismiss widget"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
});

// Export with memo - Zustand's object-based selectors prevent cascade re-renders
// Each widget only re-renders when its own data changes
export default IsolatedWidget;
