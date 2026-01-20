"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import { memo, useCallback, useState } from "react"

interface ImageItem {
  url: string
  caption?: string
  title?: string
}

interface GalleryWidgetProps {
  title?: string
  content?: string
  images?: ImageItem[]
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

const DEFAULT_IMAGES: ImageItem[] = [
  {
    url: "https://picsum.photos/seed/nature1/400/400",
    title: "Nature Scene",
    caption: "Random nature from Picsum"
  },
  {
    url: "https://picsum.photos/seed/nature2/400/400",
    title: "Landscape",
    caption: "Beautiful landscape"
  },
  {
    url: "https://picsum.photos/seed/nature3/400/400",
    title: "Water View",
    caption: "Serene water scenery"
  },
  {
    url: "https://picsum.photos/seed/nature4/400/400",
    title: "Mountain",
    caption: "Majestic mountain view"
  }
]

export const GalleryWidget = memo(function GalleryWidget({ title, content, images = DEFAULT_IMAGES, onDismiss, dragPosition, onDragEnd }: GalleryWidgetProps) {
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

      <div className="p-4">
        {title && <h3 className="text-lg font-semibold mb-2">{title}</h3>}
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
                src={images[selectedIndex]?.url}
                alt={images[selectedIndex]?.title || "Gallery image"}
                className="max-w-full max-h-[80vh] object-contain rounded-lg"
              />
              {(images[selectedIndex]?.title || images[selectedIndex]?.caption) && (
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 rounded-b-lg">
                  {images[selectedIndex]?.title && (
                    <h4 className="text-white font-semibold">{images[selectedIndex].title}</h4>
                  )}
                  {images[selectedIndex]?.caption && (
                    <p className="text-white/80 text-sm">{images[selectedIndex].caption}</p>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Thumbnail Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {images.map((image, index) => (
            <motion.button
              key={index}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative aspect-square rounded-lg overflow-hidden border border-border"
              onClick={() => setSelectedIndex(index)}
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
  )
});
