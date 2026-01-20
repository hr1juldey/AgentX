"use client";

import { motion, useMotionValue, useTransform } from "framer-motion";
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
import { memo, useCallback } from "react";

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
  onDismiss: () => void;
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
};

// Widget type to CSS color variable mapping
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

export const ToolIsland = memo(function ToolIsland({
  widget,
  position,
  isActive,
  onClick,
  onDragEnd,
  onDismiss,
}: ToolIslandProps) {
  const dragX = useMotionValue(position.x);
  const dragY = useMotionValue(position.y);

  const IconComponent = widgetIcons[widget.descriptor_type] || FileText;
  const islandColor = widgetColors[widget.descriptor_type] || "var(--island-white)";

  const handleDragEnd = useCallback(
    (_: unknown, info: { offset: { x: number; y: number } }) => {
      onDragEnd(position.x + info.offset.x, position.y + info.offset.y);
    },
    [onDragEnd, position]
  );

  const handleDismiss = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onDismiss();
    },
    [onDismiss]
  );

  return (
    <motion.div
      style={{ x: dragX, y: dragY }}
      drag
      dragElastic={0.2}
      dragMomentum={false}
      dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
      whileDrag={{ scale: 1.05, cursor: "grabbing", zIndex: 50 }}
      onDragEnd={handleDragEnd}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: isActive ? 1.05 : 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.22 }}
      className="relative"
    >
      <motion.button
        onClick={onClick}
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
        <IconComponent className="w-5 h-5 text-foreground" strokeWidth={2} />

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

        {/* Dismiss button */}
        <button
          onClick={handleDismiss}
          className="absolute -top-1 -right-1 p-1 rounded-full bg-destructive text-destructive-foreground opacity-0 hover:opacity-100 transition-opacity group-hover:opacity-100"
          aria-label="Dismiss widget"
        >
          <X className="w-3 h-3" />
        </button>
      </motion.button>

      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-popover text-popover-foreground text-xs rounded whitespace-nowrap opacity-0 hover:opacity-100 pointer-events-none transition-opacity">
        {widget.title || widget.descriptor_type}
      </div>
    </motion.div>
  );
});
