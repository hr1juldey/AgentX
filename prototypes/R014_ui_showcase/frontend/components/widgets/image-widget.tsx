"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { memo, useCallback, useState } from "react"

interface ImageWidgetProps {
  title?: string
  content?: string
  imageUrl?: string
  caption?: string
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export const ImageWidget = memo(function ImageWidget({ title, content, imageUrl, caption, onDismiss, dragPosition, onDragEnd }: ImageWidgetProps) {
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

  // Use picsum.photos for placeholder images
  const displayUrl = imageUrl || `https://picsum.photos/800/600?random=${Math.random()}`

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
      {onDismiss && (
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 p-1 rounded bg-black/50 hover:bg-black/70 transition-colors z-10"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4 text-white" />
        </button>
      )}

      {title && (
        <div className="p-4 pb-2">
          <h3 className="text-lg font-semibold">{title}</h3>
        </div>
      )}

      <div className="relative aspect-video w-full bg-muted">
        {!imageError ? (
          <img
            src={displayUrl}
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
    </motion.div>
  )
});
