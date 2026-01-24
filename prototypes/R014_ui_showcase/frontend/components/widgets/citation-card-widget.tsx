"use client"

import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react"
import { memo, useCallback, useState, useMemo } from "react"

interface Citation {
  cited_text: string
  document_index: number
  document_title?: string
  url?: string
}

interface CitationCardWidgetProps {
  citations: Citation[]
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export const CitationCardWidget = memo(function CitationCardWidget({
  citations,
  onDismiss,
  dragPosition,
  onDragEnd,
}: CitationCardWidgetProps) {
  const [expandedCards, setExpandedCards] = useState<Set<number>>(new Set())

  const handleDragEnd = useCallback(
    (_: any, info: any) => {
      onDragEnd?.(
        (dragPosition?.x || 0) + info.offset.x,
        (dragPosition?.y || 0) + info.offset.y
      )
    },
    [onDragEnd, dragPosition]
  )

  const handleDismiss = useCallback(() => {
    onDismiss?.()
  }, [onDismiss])

  const toggleCard = useCallback(
    (index: number) => {
      setExpandedCards((prev) => {
        const newSet = new Set(prev)
        if (newSet.has(index)) {
          newSet.delete(index)
        } else {
          newSet.add(index)
        }
        return newSet
      })
    },
    []
  )

  // Memoized toggle handlers to prevent re-renders in map
  const toggleHandlers = useMemo(() => {
    return citations.map((_, index) => () => toggleCard(index))
  }, [citations, toggleCard])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      drag
      dragElastic={0.1}
      dragMomentum={false}
      dragConstraints={false}
      whileDrag={{ scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className="relative bg-card border border-border rounded-lg p-4 cursor-grab shadow-lg hover:shadow-xl max-w-[400px]"
    >
      {onDismiss && (
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors"
          aria-label="Dismiss"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}

      <h3 className="font-semibold mb-3">Sources ({citations.length})</h3>

      <div className="space-y-2">
        {citations.map((citation, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
            className="border border-border rounded-lg overflow-hidden"
          >
            {/* Collapsed View */}
            <div
              className="p-3 cursor-pointer hover:bg-muted/50"
              onClick={toggleHandlers[index]}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">
                    [{index + 1}] {citation.document_title || `Source ${citation.document_index + 1}`}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{citation.cited_text}</p>
                </div>
                <button className="p-1 hover:bg-muted rounded flex-shrink-0">
                  {expandedCards.has(index) ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Expanded View */}
            <AnimatePresence>
              {expandedCards.has(index) && (
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: "auto" }}
                  exit={{ height: 0 }}
                  className="border-t border-border bg-muted/20"
                >
                  <div className="p-3">
                    <p className="text-sm">{citation.cited_text}</p>
                    {citation.url && (
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-xs text-primary hover:underline mt-2"
                      >
                        <ExternalLink className="w-3 h-3" />
                        View source
                      </a>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
})
