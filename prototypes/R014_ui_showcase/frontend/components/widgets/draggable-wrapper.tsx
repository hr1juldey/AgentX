"use client"

import { motion } from "framer-motion"
import { useRef } from "react"

interface DraggableWrapperProps {
  children: React.ReactNode
  className?: string
}

export function DraggableWrapper({ children, className = "" }: DraggableWrapperProps) {
  const constraintsRef = useRef<HTMLDivElement>(null)

  return (
    <div ref={constraintsRef} className={`relative w-full h-full min-h-[200px] ${className}`}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        transition={{ duration: 0.2 }}
        drag
        dragConstraints={constraintsRef}
        dragElastic={0.1}
        dragMomentum={false}
        whileDrag={{ scale: 1.02, cursor: "grabbing" }}
        className="relative w-fit cursor-grab shadow-lg"
        style={{ zIndex: 10 }}
      >
        {children}
      </motion.div>
    </div>
  )
}
