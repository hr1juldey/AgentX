"use client";

import { memo, useCallback } from "react";
import { motion, AnimatePresence, PanInfo } from "framer-motion";
import { X } from "lucide-react";
import type { UIDescriptor } from "@/types/widget-types";

// No-op function for optional drag handlers
const NOOP_FN = () => {};

export interface CollapsibleWidgetWrapperProps {
  descriptor: UIDescriptor;
  onDismiss: () => void;
  onDragEnd: (x: number, y: number) => void;
  onToggleCollapse: () => void;
  isExpanded: boolean;
  children: React.ReactNode;
}

/**
 * CollapsibleWidgetWrapper - Wrapper component that adds collapse/expand functionality
 * to widgets. Shows a mini "island" button when collapsed, and renders children when expanded.
 *
 * This is used in "traditional mode" (non-island mode) to provide collapse functionality
 * for widgets.
 */
export const CollapsibleWidgetWrapper = memo(function CollapsibleWidgetWrapper({
  descriptor,
  onDismiss,
  onDragEnd,
  onToggleCollapse,
  isExpanded,
  children,
}: CollapsibleWidgetWrapperProps) {
  // Widget type icons
  const getWidgetIcon = useCallback(() => {
    switch (descriptor.descriptor_type) {
      case "markdown": return "📝";
      case "card": return "📇";
      case "form": return "📋";
      case "progress": return "📊";
      case "action": return "⚡";
      case "confirmation": return "❓";
      case "image": return "🖼️";
      case "gallery": return "🖼️";
      case "chart": return "📈";
      case "search-result": return "🔍";
      case "hop-progress": return "🔄";
      case "citation-card": return "📚";
      default: return "📦";
    }
  }, [descriptor.descriptor_type]);

  // Memoized handlers to prevent re-renders
  const handleCollapsedDragEnd = useCallback((_: unknown, info: PanInfo) => {
    onDragEnd(
      (descriptor.x || 0) + info.offset.x,
      (descriptor.y || 0) + info.offset.y
    );
  }, [onDragEnd, descriptor.x, descriptor.y]);

  const handleDismissClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onDismiss();
  }, [onDismiss]);

  return (
    <motion.div
      layout
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
    >
      {/* Collapsed mini island */}
      <AnimatePresence mode="wait">
        {!isExpanded ? (
          <motion.div
            key="collapsed"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="relative"
          >
            <motion.button
              drag
              dragElastic={0.2}
              dragMomentum={false}
              dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
              whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
              onDragEnd={handleCollapsedDragEnd}
              onClick={onToggleCollapse}
              style={{ x: descriptor.x || 0, y: descriptor.y || 0 }}
              className="relative bg-card border border-border rounded-full cursor-grab shadow-lg hover:shadow-xl px-4 py-2 flex items-center gap-2 hover:bg-muted/50 transition-colors"
            >
              <span className="text-lg">{getWidgetIcon()}</span>
              <span className="text-sm font-medium truncate max-w-[120px]">
                {descriptor.title || descriptor.descriptor_type}
              </span>
              {/* Dismiss button */}
              <button
                onClick={handleDismissClick}
                className="p-1 rounded-full hover:bg-destructive/10 hover:text-destructive transition-colors"
                aria-label="Dismiss"
              >
                <X className="w-3 h-3" />
              </button>
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            key="expanded"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
});
