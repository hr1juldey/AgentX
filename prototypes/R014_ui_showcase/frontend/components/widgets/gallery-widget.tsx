"use client"

import { motion, AnimatePresence } from "framer-motion"
import { X, Images, ChevronDown } from "lucide-react"
import { memo, useCallback, useState, useMemo } from "react"

interface ImageItem {
  url: string
  caption?: string
  title?: string
}

interface GalleryWidgetProps {
  title?: string
  content?: string
  images?: ImageItem[]
  collapsed?: boolean
  onToggleCollapse?: () => void
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  descriptor_id?: string
}

export const GalleryWidget = memo(function GalleryWidget({
  title,
  content,
  images,
  collapsed = false,
  onToggleCollapse,
  onDismiss,
  dragPosition,
  onDragEnd,
  descriptor_id
}: GalleryWidgetProps) {
  const handleDragEnd = useCallback((_: any, info: any) => {
    onDragEnd?.(
      (dragPosition?.x || 0) + info.offset.x,
      (dragPosition?.y || 0) + info.offset.y
    );
  }, [onDragEnd, dragPosition]);

  const handleDismiss = useCallback(() => {
    onDismiss?.();
  }, [onDismiss]);

  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)

  // Use stable images from metadata if available, otherwise generate seeded defaults
  const displayImages = useMemo(() => {
    if (images && images.length > 0) {
      return images;  // Use images from backend metadata
    }
    // Fallback to seeded images based on descriptor_id
    const seed = descriptor_id || 'gallery';
    return [
      { url: `https://picsum.photos/seed/${seed}1/400/400`, title: "Image 1", caption: "Gallery image 1" },
      { url: `https://picsum.photos/seed/${seed}2/400/400`, title: "Image 2", caption: "Gallery image 2" },
      { url: `https://picsum.photos/seed/${seed}3/400/400`, title: "Image 3", caption: "Gallery image 3" },
      { url: `https://picsum.photos/seed/${seed}4/400/400`, title: "Image 4", caption: "Gallery image 4" },
    ];
  }, [images, descriptor_id]);

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
          <Images className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">{title || "Gallery"}</span>
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

      {/* Gallery Content - Collapsible with smart animation */}
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
            <div className="p-4">
              {content && <p className="text-sm text-muted-foreground mb-4">{content}</p>}

              {/* Lightbox */}
              {selectedIndex !== null && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
                  onClick={() => setSelectedIndex(null)}
                >
                  <button
                    onClick={() => setSelectedIndex(null)}
                    className="absolute top-4 right-4 p-2 rounded bg-white/10 hover:bg-white/20 transition-colors"
                    aria-label="Close"
                  >
                    <X className="w-6 h-6 text-white" />
                  </button>
                  <div className="max-w-4xl max-h-[80vh] relative" onClick={(e) => e.stopPropagation()}>
                    <img
                      src={displayImages[selectedIndex]?.url}
                      alt={displayImages[selectedIndex]?.title || "Gallery image"}
                      className="max-w-full max-h-[80vh] object-contain rounded-lg"
                    />
                    {(displayImages[selectedIndex]?.title || displayImages[selectedIndex]?.caption) && (
                      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 rounded-b-lg">
                        {displayImages[selectedIndex]?.title && (
                          <h4 className="text-white font-semibold">{displayImages[selectedIndex].title}</h4>
                        )}
                        {displayImages[selectedIndex]?.caption && (
                          <p className="text-white/80 text-sm">{displayImages[selectedIndex].caption}</p>
                        )}
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Thumbnail Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {displayImages.map((image, index) => (
                  <motion.button
                    key={index}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="relative aspect-square rounded-lg overflow-hidden border border-border"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedIndex(index);
                    }}
                  >
                    <img
                      src={image.url}
                      alt={image.title || `Gallery image ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-0 hover:opacity-100 transition-opacity">
                      <div className="absolute bottom-0 left-0 right-0 p-2">
                        {image.title && (
                          <p className="text-white text-xs font-medium truncate">{image.title}</p>
                        )}
                      </div>
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
});
