"use client";

import { motion, useMotionValue } from "framer-motion";
import { Search, Activity, FileSearch } from "lucide-react";
import { memo, useCallback, useEffect, useRef, useState } from "react";
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

interface UIDescriptor {
  descriptor_id: string;
  descriptor_type: string;
  title?: string;
  x?: number;
  y?: number;
  collapsed?: boolean;
  metadata?: Record<string, unknown>;
}

interface ToolIslandProps {
  widget: UIDescriptor;
  position: { x: number; y: number };
  isActive: boolean;
  onClick: () => void;
  onDragEnd: (x: number, y: number) => void;
}

// Widget type to icon mapping
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
  "search-result": Search,
  "hop-progress": Activity,
  "citation-card": FileSearch,
};

// Widget type to CSS color variable mapping (with hsl() wrapper)
const widgetColors: Record<string, string> = {
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

export const ToolIsland = memo(function ToolIsland({
  widget,
  position,
  isActive,
  onClick,
  onDragEnd,
}: ToolIslandProps) {
  const dragX = useMotionValue(position.x);
  const dragY = useMotionValue(position.y);
  const dragDistanceRef = useRef(0);

  const IconComponent = widgetIcons[widget.descriptor_type] || FileText;
  const islandColor = widgetColors[widget.descriptor_type] || "hsl(var(--island-white))";

  // Sync motion values with position prop changes
  useEffect(() => {
    dragX.set(position.x);
    dragY.set(position.y);
  }, [position.x, position.y, dragX, dragY]);

  const handleDrag = useCallback(() => {
    dragDistanceRef.current++;
    if (dragDistanceRef.current === 1) {
      console.log(`🖱️ [ISLAND DRAG START] ${widget.descriptor_id}`);
    }
  }, []);

  const handleDragEnd = useCallback(
    (_: unknown, info: { offset: { x: number; y: number } }) => {
      const distance = Math.sqrt(info.offset.x ** 2 + info.offset.y ** 2);
      console.log(`🖱️ [ISLAND DRAG END] ${widget.descriptor_id} distance: ${distance.toFixed(1)}px, offset: {x: ${info.offset.x.toFixed(1)}, y: ${info.offset.y.toFixed(1)}}`);
      // Pass only the offset (consistent with card/full states)
      onDragEnd(info.offset.x, info.offset.y);
    },
    [onDragEnd, widget.descriptor_id]
  );

  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      console.log(`👆 [ISLAND CLICK] ${widget.descriptor_id}, dragDistance: ${dragDistanceRef.current}`);
      // Only trigger onClick if there was no significant drag
      if (dragDistanceRef.current < 5) {
        console.log(`👆 [ISLAND CLICK] Triggering onClick for ${widget.descriptor_id}`);
        onClick();
      } else {
        console.log(`👆 [ISLAND CLICK] Ignored (was a drag) for ${widget.descriptor_id}`);
      }
      dragDistanceRef.current = 0;
    },
    [onClick, widget.descriptor_id]
  );

  return (
    <motion.div
      style={{ x: dragX, y: dragY }}
      drag
      dragElastic={0}
      dragMomentum={false}
      whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
      onDrag={handleDrag}
      onDragEnd={handleDragEnd}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: isActive ? 1.05 : 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.22 }}
      className="fixed pointer-events-auto"
    >
      <div className="relative group">
        <motion.button
          onClick={handleClick}
          className={`
            relative rounded-full shadow-lg hover:shadow-xl
            flex items-center justify-center
            transition-all duration-220
            ${isActive ? "ring-2 ring-primary" : ""}
          `}
          style={{
            width: "var(--island-diameter)",
            height: "var(--island-diameter)",
            background: islandColor,
          }}
          whileHover={{ y: -6 }}
          whileTap={{ scale: 0.95 }}
          aria-label={`${widget.descriptor_type} widget ${widget.title ? `: ${widget.title}` : ""}`}
        >
          {/* Icon */}
          <IconComponent className="w-5 h-5 text-[hsl(var(--island-icon-color))]" strokeWidth={2} />

          {/* Active glow */}
          {isActive && (
            <motion.div
              className="absolute inset-0 rounded-full"
              style={{ background: islandColor }}
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
      </div>

      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded whitespace-nowrap opacity-0 hover:opacity-100 pointer-events-none transition-opacity">
        {widget.title || widget.descriptor_type}
      </div>
    </motion.div>
  );
});
