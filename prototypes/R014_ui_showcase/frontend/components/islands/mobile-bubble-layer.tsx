"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
import {
  FileText,
  Layout,
  ClipboardList,
  BarChart3,
  Zap,
  HelpCircle,
  Image as ImageIcon,
  Images,
  LineChart,
} from "lucide-react";
import React, { memo, useCallback, useState, useMemo } from "react";
import { useWidgetStore } from "@/store/widget-store";

interface UIDescriptor {
  descriptor_id: string;
  descriptor_type: string;
  title?: string;
}

interface MobileBubbleLayerProps {
  expandedIds: Set<string>;
  onExpand: (id: string) => void;
  onDismiss: (id: string) => void;
}

// Widget type to icon mapping (same as ToolIsland)
const widgetIcons: Record<string, React.ElementType> = {
  markdown: FileText,
  card: Layout,
  form: ClipboardList,
  progress: BarChart3,
  action: Zap,
  confirmation: HelpCircle,
  image: ImageIcon,
  gallery: Images,
  chart: LineChart,
};

// Widget type to CSS color variable mapping (same as ToolIsland)
const widgetColors: Record<string, string> = {
  markdown: "var(--island-markdown)",
  card: "var(--island-card)",
  form: "var(--island-form)",
  progress: "var(--island-progress)",
  action: "var(--island-action)",
  confirmation: "var(--island-confirmation)",
  image: "var(--island-image)",
  gallery: "var(--island-gallery)",
  chart: "var(--island-chart)",
};

const BUBBLE_SIZE = 48; // 48px for mobile (vs 56px desktop)
const MAX_BUBBLES = 6;
const BUBBLE_SPACING = 60;
const EDGE_MARGIN = 16;

/**
 * MobileBubbleLayer - Mobile-only floating bubble layout
 *
 * KEY DESIGN PRINCIPLE (Jira/Linear style isolation):
 * - Reads widgets directly from Zustand store (NO props passed from parent)
 * - Parent re-renders DO NOT affect this component
 * - Only re-renders when the specific widget data it subscribes to changes
 * - This prevents cascade re-renders when widgets are added/removed
 *
 * Features:
 * - 48px bubbles (vs 56px desktop)
 * - Vertical stack along right edge
 * - Edge snapping on drag end
 * - Max 6 islands constraint
 * - Max 4 expanded panels (mobile limit)
 * - Visible only on mobile (md:hidden breakpoint)
 */
const MAX_EXPANDED_MOBILE = 4;

export const MobileBubbleLayer = memo(function MobileBubbleLayer({
  expandedIds,
  onExpand,
  onDismiss,
}: MobileBubbleLayerProps) {
  // Subscribe to widgetIds array - uses atomic state pattern for stable reference
  const widgetIds = useWidgetStore((s) => s.widgetIds);

  // Derive widgets array from widgetIds
  const widgets = useMemo(() => {
    return widgetIds.map(id => {
      const dataKey = `widget_${id}_data`;
      return useWidgetStore.getState()[dataKey] as UIDescriptor;
    });
  }, [widgetIds]);

  const [bubblePositions, setBubblePositions] = useState<Record<string, { x: number; y: number }>>({});

  // Only show up to MAX_BUBBLES
  const visibleWidgets = useMemo(
    () => widgets.slice(0, MAX_BUBBLES),
    [widgets]
  );

  const handleDragEnd = useCallback(
    (id: string, _: unknown, info: { offset: { x: number; y: number } }) => {
      const currentPos = bubblePositions[id] || { x: 0, y: 0 };
      const newX = currentPos.x + info.offset.x;
      const newY = currentPos.y + info.offset.y;

      // Edge snapping: snap to left or right edge
      if (typeof window !== "undefined") {
        const viewportWidth = window.innerWidth;
        const snapToRight = newX > viewportWidth / 2;

        setBubblePositions((prev) => ({
          ...prev,
          [id]: {
            x: snapToRight ? viewportWidth - EDGE_MARGIN - BUBBLE_SIZE / 2 : EDGE_MARGIN + BUBBLE_SIZE / 2,
            y: Math.max(EDGE_MARGIN, Math.min(newY, window.innerHeight - EDGE_MARGIN - BUBBLE_SIZE)),
          },
        }));
      }
    },
    [bubblePositions]
  );

  const handleClick = useCallback(
    (id: string) => {
      if (expandedIds.has(id)) {
        // Toggle collapse if clicking the expanded bubble
        onExpand(id); // Parent will handle removal from Set
      } else if (expandedIds.size < MAX_EXPANDED_MOBILE) {
        // Expand if under limit
        onExpand(id);
      } else {
        console.warn(`Maximum ${MAX_EXPANDED_MOBILE} widgets can be expanded on mobile`);
      }
    },
    [expandedIds, onExpand]
  );

  const handleDismiss = useCallback(
    (e: React.MouseEvent, id: string) => {
      e.stopPropagation();
      onDismiss(id);
    },
    [onDismiss]
  );

  // Memoized handlers map to prevent re-renders in map() callback
  const widgetHandlers = useMemo(() => {
    const handlers: Record<string, {
      onDragEnd: (_: unknown, info: { offset: { x: number; y: number } }) => void;
      onClick: () => void;
      onDismiss: (e: React.MouseEvent) => void;
    }> = {};

    visibleWidgets.forEach(widget => {
      const id = widget.descriptor_id;
      handlers[id] = {
        onDragEnd: (_: unknown, info: { offset: { x: number; y: number } }) => handleDragEnd(id, _, info),
        onClick: () => handleClick(id),
        onDismiss: (e: React.MouseEvent) => handleDismiss(e, id),
      };
    });

    return handlers;
  }, [visibleWidgets, handleDragEnd, handleClick, handleDismiss]);

  return (
    <div className="md:hidden fixed inset-0 pointer-events-none z-40">
      <AnimatePresence>
        {visibleWidgets.map((widget, index) => {
          const IconComponent = widgetIcons[widget.descriptor_type] || FileText;
          const islandColor = widgetColors[widget.descriptor_type] || "var(--island-white)";
          const isExpanded = expandedIds.has(widget.descriptor_id);

          // Default position along right edge
          const defaultPosition = {
            x: typeof window !== "undefined" ? window.innerWidth - EDGE_MARGIN - BUBBLE_SIZE / 2 : 300,
            y: EDGE_MARGIN + index * BUBBLE_SPACING,
          };

          const position = bubblePositions[widget.descriptor_id] || defaultPosition;
          const handlers = widgetHandlers[widget.descriptor_id];

          // DIAGNOSTIC: Log bubble positions on render (outside effect, in render)
          // This helps track if bubbles are shifting due to index changes
          if (process.env.NODE_ENV === 'development') {
            const hasSavedPosition = bubblePositions[widget.descriptor_id] !== undefined;
            console.log(`[Bubble ${widget.descriptor_id}] idx=${index} pos=(${position.x.toFixed(0)}, ${position.y.toFixed(0)}) ${hasSavedPosition ? '(saved)' : '(default-index-based)'}`);
          }

          return (
            <motion.div
              key={widget.descriptor_id}
              style={{ x: position.x, y: position.y }}
              drag
              dragElastic={0.2}
              dragMomentum={false}
              onDragEnd={handlers?.onDragEnd}
              whileDrag={{ scale: 1.05, cursor: "grabbing" }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: isExpanded ? 1.1 : 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.22 }}
              className="absolute pointer-events-auto"
            >
              <div className="relative">
                <motion.button
                  onClick={handlers?.onClick}
                  className="relative rounded-full shadow-lg"
                  style={{
                    width: `${BUBBLE_SIZE}px`,
                    height: `${BUBBLE_SIZE}px`,
                    background: islandColor,
                  }}
                  whileTap={{ scale: 0.95 }}
                  aria-label={`${widget.descriptor_type} widget ${widget.title ? `: ${widget.title}` : ""}`}
                >
                  {/* Icon */}
                  <IconComponent className="w-5 h-5 text-foreground absolute inset-0 m-auto" strokeWidth={2} />

                  {/* Expanded indicator */}
                  {isExpanded && (
                    <motion.div
                      className="absolute inset-0 rounded-full ring-2 ring-primary"
                      animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.5, 0, 0.5],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut",
                      }}
                    />
                  )}
                </motion.button>

                {/* Dismiss button - outside the main button */}
                <button
                  onClick={handlers?.onDismiss}
                  className="absolute -top-1 -right-1 p-1 rounded-full bg-destructive text-destructive-foreground opacity-0 hover:opacity-100 transition-opacity shadow-sm"
                  aria-label="Dismiss widget"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* Overflow indicator */}
      {widgets.length > MAX_BUBBLES && (
        <div className="absolute bottom-4 right-4 bg-muted px-3 py-1 rounded-full text-xs text-muted-foreground">
          +{widgets.length - MAX_BUBBLES} more
        </div>
      )}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison for MobileBubbleLayer
  // Only re-render if expandedIds Set actually changed
  // This prevents re-renders when parent's local state changes but expandedIds didn't
  if (prevProps.expandedIds.size !== nextProps.expandedIds.size) {
    return false;
  }
  const prevIds = Array.from(prevProps.expandedIds);
  const nextIds = Array.from(nextProps.expandedIds);
  for (let i = 0; i < prevIds.length; i++) {
    if (prevIds[i] !== nextIds[i]) {
      return false;
    }
  }
  // If all IDs match, don't re-render
  return true;
});
