"use client"

import { motion } from "framer-motion"
import { CheckCircle2, ExternalLink, X } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import { memo, useCallback, useMemo } from "react"

interface Citation {
  cited_text: string
  document_index: number
  document_title?: string
  url?: string
}

interface SearchResultWidgetProps {
  content: string
  citations?: Citation[]
  metadata?: Record<string, unknown>
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

function stripMarkdownWrapper(content: string): string {
  let cleaned = content

  if (cleaned.startsWith("```markdown")) {
    cleaned = cleaned.slice(11)
  } else if (cleaned.startsWith("```")) {
    cleaned = cleaned.slice(3)
  }

  cleaned = cleaned.trimStart()

  if (cleaned.endsWith("```")) {
    cleaned = cleaned.slice(0, -3)
  }

  cleaned = cleaned.trimEnd()

  return cleaned
}

export const SearchResultWidget = memo(function SearchResultWidget({
  content,
  citations = [],
  metadata,
  onDismiss,
  dragPosition,
  onDragEnd,
}: SearchResultWidgetProps) {
  // Extract confidence with proper type guard
  const confidence = useMemo(() => {
    if (metadata?.confidence && typeof metadata.confidence === "string") {
      return metadata.confidence
    }
    return null
  }, [metadata])

  const cleanedContent = useMemo(() => stripMarkdownWrapper(content), [content])

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
      className="relative bg-card border border-border rounded-lg p-6 cursor-grab shadow-lg hover:shadow-xl max-w-[600px]"
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

      {/* Header with confidence badge */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-green-500" />
          <h3 className="text-lg font-semibold">Answer</h3>
        </div>
        {confidence && (
          <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
            {confidence} confidence
          </span>
        )}
      </div>

      {/* Answer content with markdown */}
      <div className="text-sm leading-relaxed max-h-[50vh] overflow-y-auto pr-2 mb-4">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 className="text-xl font-semibold mb-3">{children}</h1>,
            h2: ({ children }) => <h2 className="text-lg font-semibold mb-2">{children}</h2>,
            p: ({ children }) => <p className="mb-3">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
            a: ({ href, children }) => (
              <a href={href} className="text-primary underline" target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
          }}
        >
          {cleanedContent}
        </ReactMarkdown>
      </div>

      {/* Citations footer */}
      {citations.length > 0 && (
        <div className="border-t border-border pt-4">
          <p className="text-xs text-muted-foreground mb-2">{citations.length} sources</p>
          <div className="flex flex-wrap gap-2">
            {citations.slice(0, 5).map((citation, index) => (
              <button
                key={index}
                className="text-xs px-2 py-1 rounded bg-muted hover:bg-muted/80 transition-colors"
                title={citation.document_title}
              >
                [{index + 1}]
              </button>
            ))}
            {citations.length > 5 && (
              <span className="text-xs px-2 py-1 text-muted-foreground">
                +{citations.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}
    </motion.div>
  )
})
