"use client"

import { motion, AnimatePresence } from "framer-motion"
import { ChevronDown, ChevronUp, FileText, Loader2, Search } from "lucide-react"
import { memo, useCallback, useState } from "react"

interface HopEvent {
  event_type: string
  hop_number: number
  total_hops: number
  message: string
  progress: number
  eta_seconds?: number
  documents_found?: number
  query_used?: string
  reflection_reasoning?: string
}

interface HopProgressWidgetProps {
  events: HopEvent[]
  onDismiss?: () => void
  dragPosition?: { x: number; y: number }
  onDragEnd?: (x: number, y: number) => void
  disableDrag?: boolean // When true, widget is not draggable (for embedded use in IsolatedWidget)
}

export const HopProgressWidget = memo(function HopProgressWidget({
  events,
  onDismiss,
  dragPosition,
  onDragEnd,
  disableDrag = false
}: HopProgressWidgetProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const latestEvent = events[events.length - 1]

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

  const handleToggle = useCallback(() => {
    setIsExpanded((prev) => !prev)
  }, [])

  const isComplete = latestEvent?.event_type === "hop_complete" || latestEvent?.event_type === "search_complete"
  const progress = latestEvent?.progress ?? 0

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      drag={disableDrag ? false : undefined}
      dragElastic={0.1}
      dragMomentum={false}
      dragConstraints={false}
      whileDrag={disableDrag ? undefined : { scale: 1.02, cursor: "grabbing", zIndex: 9999 }}
      onDragEnd={disableDrag ? undefined : handleDragEnd}
      style={{ x: dragPosition?.x || 0, y: dragPosition?.y || 0 }}
      className={`relative bg-card border border-border rounded-lg p-4 shadow-lg hover:shadow-xl max-w-[500px] ${disableDrag ? '' : 'cursor-grab'}`}
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

      {/* Collapsed View: Compact status with round progress ring */}
      <div>
        <div className="flex items-center gap-3">
          {/* Round progress indicator */}
          <div className="relative w-12 h-12 flex-shrink-0">
            <svg className="absolute inset-0 w-full h-full transform -rotate-90">
              <circle
                cx="50%"
                cy="50%"
                r={20}
                stroke="hsl(var(--border))"
                strokeWidth="4"
                fill="none"
              />
              <motion.circle
                cx="50%"
                cy="50%"
                r={20}
                stroke="hsl(var(--primary))"
                strokeWidth="4"
                fill="none"
                strokeDasharray={2 * Math.PI * 20}
                strokeDashoffset={2 * Math.PI * 20 * (1 - progress)}
                strokeLinecap="round"
                animate={{ strokeDashoffset: 2 * Math.PI * 20 * (1 - progress) }}
                transition={{ duration: 0.3 }}
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              {isComplete ? (
                <FileText className="w-5 h-5 text-green-500" />
              ) : (
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
              )}
            </div>
          </div>

          {/* Status text */}
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm truncate">{latestEvent?.message || "Preparing..."}</p>
            <p className="text-xs text-muted-foreground">
              Hop {latestEvent?.hop_number || 0} of {latestEvent?.total_hops || 0}
              {latestEvent?.eta_seconds && ` • ${latestEvent.eta_seconds.toFixed(1)}s ETA`}
            </p>
          </div>

          {/* Expand/collapse button */}
          <button
            onClick={handleToggle}
            className="p-2 hover:bg-muted rounded flex-shrink-0"
            aria-label={isExpanded ? "Collapse" : "Expand"}
          >
            {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>

        {/* Progress bar */}
        <div className="mt-3 h-2 bg-muted rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-primary"
            initial={{ width: 0 }}
            animate={{ width: `${progress * 100}%` }}
            transition={{ duration: 0.3 }}
          />
        </div>
      </div>

      {/* Expanded View: Detailed hop-by-hop */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-4 overflow-hidden"
          >
            <div className="border-t border-border pt-4 space-y-3">
              {events.map((event, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex gap-3 text-sm"
                >
                  <div className="flex flex-col items-center">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        event.event_type === "hop_complete"
                          ? "bg-green-500"
                          : event.event_type === "hop_start"
                            ? "bg-blue-500"
                            : "bg-yellow-500"
                      }`}
                    />
                    {index < events.length - 1 && <div className="w-0.5 h-full bg-border my-1" />}
                  </div>
                  <div className="flex-1 pb-3">
                    <p className="font-medium">{event.message}</p>
                    {event.query_used && (
                      <p className="text-xs text-muted-foreground mt-1">Query: "{event.query_used}"</p>
                    )}
                    {event.documents_found !== undefined && event.documents_found > 0 && (
                      <p className="text-xs text-muted-foreground">{event.documents_found} documents found</p>
                    )}
                    {event.reflection_reasoning && (
                      <p className="text-xs text-muted-foreground mt-1 italic">{event.reflection_reasoning}</p>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
})
