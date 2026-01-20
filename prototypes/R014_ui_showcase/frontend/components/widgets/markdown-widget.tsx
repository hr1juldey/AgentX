"use client"

import { motion } from "framer-motion"
import { X } from "lucide-react"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface MarkdownWidgetProps {
  content: string
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
}

export function MarkdownWidget({ content, onDismiss, dragPosition, onDragEnd }: MarkdownWidgetProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
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
      className="relative bg-card border border-border rounded-lg p-6 cursor-grab shadow-lg hover:shadow-xl"
    >
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="absolute top-2 right-2 p-1 rounded hover:bg-muted transition-colors"
          aria-label="Dismiss"
        >
          <X className="w-4 h-4" />
        </button>
      )}
      <div className="text-sm leading-relaxed space-y-3">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            h1: ({ children }) => <h1 className="text-xl font-semibold mb-3">{children}</h1>,
            h2: ({ children }) => <h2 className="text-lg font-semibold mb-2">{children}</h2>,
            h3: ({ children }) => <h3 className="text-base font-semibold mb-2">{children}</h3>,
            p: ({ children }) => <p className="mb-3">{children}</p>,
            ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
            ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
            li: ({ children }) => <li>{children}</li>,
            code: ({ className, children }) => {
              const isInline = !className?.includes('block');
              return isInline ? (
                <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
              ) : (
                <code className="bg-muted px-3 py-2 rounded text-xs font-mono block overflow-x-auto">{children}</code>
              );
            },
            pre: ({ children }) => <pre className="bg-muted p-3 rounded mb-3 overflow-x-auto">{children}</pre>,
            blockquote: ({ children }) => (
              <blockquote className="border-l-3 border-muted-foreground pl-3 text-muted-foreground mb-3">
                {children}
              </blockquote>
            ),
            a: ({ href, children }) => (
              <a href={href} className="text-primary underline" target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            ),
            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
            em: ({ children }) => <em className="italic">{children}</em>,
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </motion.div>
  )
}
