"use client"
import { memo, useCallback } from "react"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ActionWidgetProps {
  title?: string
  content?: string
  buttonText?: string
  variant?: "default" | "destructive" | "outline"
  onAction?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  disableDrag?: boolean // When true, widget is not draggable (for embedded use in IsolatedWidget)
}

export const ActionWidget = memo(function ActionWidget({
  title,
  content,
  buttonText = "Click Me",
  variant = "default",
  onAction,
  onDismiss,
  dragPosition,
  onDragEnd,
  disableDrag = false
}: ActionWidgetProps) {
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);


  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.15 }}
      drag={disableDrag ? false : undefined}
      dragElastic={0.2}
      dragMomentum={false}
      dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
      whileDrag={disableDrag ? undefined : { scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={disableDrag ? undefined : handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className={`relative bg-card shadow-lg hover:shadow-xl border border-border rounded-lg p-6 text-center ${disableDrag ? '' : 'cursor-grab'}`}
    >
      {onDismiss && (
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
      {content && <p className="text-sm text-muted-foreground mb-4">{content}</p>}
      <Button
        variant={variant}
        onClick={onAction}
        className="w-full"
      >
        {buttonText}
      </Button>
    </motion.div>
  );
});
