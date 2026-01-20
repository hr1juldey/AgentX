"use client";

import { motion, AnimatePresence, useMotionValue } from "framer-motion";
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
import { memo, useCallback, useState } from "react";

interface UIDescriptor {
  descriptor_id: string;
  descriptor_type: string;
  title?: string;
}

interface MobileBubbleLayerProps {
  widgets: UIDescriptor[];
  expandedId: string | null;
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
 * Features:
 * - 48px bubbles (vs 56px desktop)
 * - Vertical stack along right edge
 * - Edge snapping on drag end
 * - Max 6 islands constraint
 * - 1-2 expanded panels max
 * - Visible only on mobile (md:hidden breakpoint)
 */
export const MobileBubbleLayer = memo(function MobileBubbleLayer({
  widgets,
  expandedId,
  onExpand,
  onDismiss,
}: MobileBubbleLayerProps) {
  const [bubblePositions, setBubblePositions] = useState<Record<string, { x: number; y: number }>>({});

  // Only show up to MAX_BUBBLES
  const visibleWidgets = widgets.slice(0, MAX_BUBBLES);

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
      if (expandedId === id) {
        // If clicking the expanded bubble, do nothing (close is handled elsewhere)
        return;
      }
      onExpand(id);
    },
    [expandedId, onExpand]
  );

  const handleDismiss = useCallback(
    (e: React.MouseEvent, id: string) => {
      e.stopPropagation();
      onDismiss(id);
    },
    [onDismiss]
  );

  return (
    <div className="md:hidden fixed inset-0 pointer-events-none z-40">
      <AnimatePresence>
        {visibleWidgets.map((widget, index) => {
          const IconComponent = widgetIcons[widget.descriptor_type] || FileText;
          const islandColor = widgetColors[widget.descriptor_type] || "var(--island-white)";
          const isExpanded = expandedId === widget.descriptor_id;

          // Default position along right edge
          const defaultPosition = {
            x: typeof window !== "undefined" ? window.innerWidth - EDGE_MARGIN - BUBBLE_SIZE / 2 : 300,
            y: EDGE_MARGIN + index * BUBBLE_SPACING,
          };

          const position = bubblePositions[widget.descriptor_id] || defaultPosition;

          return (
            <motion.div
              key={widget.descriptor_id}
              style={{ x: position.x, y: position.y }}
              drag
              dragElastic={0.2}
              dragMomentum={false}
              onDragEnd={(_, info) => handleDragEnd(widget.descriptor_id, _, info)}
              whileDrag={{ scale: 1.05, cursor: "grabbing" }}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: isExpanded ? 1.1 : 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              transition={{ duration: 0.22 }}
              className="absolute pointer-events-auto"
            >
              <motion.button
                onClick={() => handleClick(widget.descriptor_id)}
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

                {/* Dismiss button */}
                <button
                  onClick={(e) => handleDismiss(e, widget.descriptor_id)}
                  className="absolute -top-1 -right-1 p-1 rounded-full bg-destructive text-destructive-foreground opacity-0 hover:opacity-100 transition-opacity"
                  aria-label="Dismiss widget"
                >
                  <X className="w-3 h-3" />
                </button>
              </motion.button>
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
});
