"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Image as ImageIcon, ChevronDown } from "lucide-react"
import { memo, useCallback, useState, useMemo } from "react"

interface ImageWidgetProps {
  title?: string
  content?: string
  imageUrl?: string
  caption?: string
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  descriptor_id?: string
}

export const ImageWidget = memo(function ImageWidget({
  title,
  content,
  imageUrl,
  caption,
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd,
  descriptor_id
}: ImageWidgetProps) {
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  const [imageError, setImageError] = useState(false)

  // Use stable image URL (generated once on mount, uses seed for stability)
  const stableImageUrl = useMemo(() => {
    if (imageUrl) return imageUrl;

    // Use descriptor_id as seed for stability
    const seed = descriptor_id || 'default';
    return `https://picsum.photos/seed/${seed}/800/600`;
  }, [imageUrl, descriptor_id]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.25 }}
      drag
      dragElastic={0.2}
      dragMomentum={false}
      dragConstraints={{ left: -500, right: 500, top: -500, bottom: 500 }}
      whileDrag={{ scale: 1.02, rotate: 1, cursor: "grabbing", zIndex: 50 }}
      onDragEnd={(_, info) => onDragEnd?.(
        (dragPosition?.x || 0) + info.offset.x,
        (dragPosition?.y || 0) + info.offset.y
      )}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card cursor-grab shadow-lg hover:shadow-xl border border-border rounded-lg overflow-hidden"
    >
      {/* Widget Header - Click to toggle (Jira-style) */}
      <div
        className="flex items-center justify-between px-4 py-2 border-b bg-muted/30 cursor-pointer hover:bg-muted/50"
        onClick={() => onToggleCollapse?.()}
      >
        <div className="flex items-center gap-2">
          <ImageIcon className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">{title || "Image"}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Chevron indicator - rotates based on collapsed state */}
          <motion.div
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          </motion.div>

          {/* Dismiss button - stopPropagation to prevent collapse */}
          {onDismiss && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                handleDismiss();
              }}
              className="p-1 rounded hover:bg-destructive/10 hover:text-destructive transition-colors"
              aria-label="Dismiss"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Image Content - Collapsible with smart animation */}
      <AnimatePresence initial={false} mode="wait">
        {!collapsed && (
          <motion.div
            layout="position"
            initial={{ height: 0, opacity: 0, scaleY: 0.95 }}
            animate={{ height: "auto", opacity: 1, scaleY: 1 }}
            exit={{ height: 0, opacity: 0, scaleY: 0.95 }}
            transition={{
              height: { type: "spring", stiffness: 400, damping: 30 },
              opacity: { duration: 0.15 },
              scaleY: { type: "spring", stiffness: 400, damping: 30 }
            }}
            style={{ originY: 0 }}
            className="overflow-hidden"
          >
            <div>
              <div className="relative aspect-video w-full bg-muted">
                {!imageError ? (
                  <img
                    src={stableImageUrl}
                    alt={caption || title || "Image"}
                    className="w-full h-full object-cover"
                    onError={() => setImageError(true)}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-muted-foreground">
                    <div className="text-center">
                      <p className="text-4xl mb-2">🖼️</p>
                      <p className="text-sm">Image unavailable</p>
                    </div>
                  </div>
                )}
              </div>

              {(caption || content) && (
                <div className="p-4">
                  {caption && <p className="text-sm text-muted-foreground italic mb-2">{caption}</p>}
                  {content && <p className="text-sm leading-relaxed">{content}</p>}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
});
