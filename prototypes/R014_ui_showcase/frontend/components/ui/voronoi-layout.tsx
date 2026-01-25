"use client"

import { useEffect, useRef, useCallback } from "react"
import { motion, useMotionValue } from "framer-motion"
import { LAYOUT_PHYSICS } from "@/constants/layout-physics"
import { calculateRepulsion, calculateAttraction, applyBoundaryConstraints } from "@/lib/force-calculations"

interface WidgetPosition {
  id: string
  x: number
  y: number
  width: number
  height: number
}

interface VoronoiLayoutProps {
  widgets: WidgetPosition[]
  onPositionsUpdate: (positions: Map<string, { x: number; y: number }>) => void
  children?: React.ReactNode
}

/**
 * Voronoi-based collision detection and layout system.
 *
 * This component implements a force-directed layout algorithm that:
 * 1. Repels widgets from each other to prevent overlap (Voronoi-style repulsion)
 * 2. Attracts widgets toward the center to keep them visible
 * 3. Smoothly animates position updates using physics-based forces
 *
 * The result is an even spread of widgets across the available screen space
 * with automatic collision avoidance.
 *
 * EXTRACTED: Physics constants and force calculation functions
 * See: /constants/layout-physics.ts and /lib/force-calculations.ts
 */
export function VoronoiLayout({ widgets, onPositionsUpdate, children }: VoronoiLayoutProps) {
  const positionsRef = useRef<Map<string, { x: number; y: number }>>(new Map())
  const animationFrameRef = useRef<number | null>(null)
  const isLayoutActiveRef = useRef(false)
  const onPositionsUpdateRef = useRef(onPositionsUpdate)
  const lastNotifiedPositionsRef = useRef<Map<string, { x: number; y: number }>>(new Map())

  // Keep the ref updated when onPositionsUpdate changes
  useEffect(() => {
    onPositionsUpdateRef.current = onPositionsUpdate
  }, [onPositionsUpdate])

  // EXTRACTED: calculateRepulsion, calculateAttraction, applyBoundaryConstraints
  // See: /lib/force-calculations.ts

  /**
   * Main layout simulation step.
   * Calculates forces and updates widget positions.
   */
  const simulateLayout = useCallback(() => {
    if (widgets.length === 0) return

    const viewportWidth = window.innerWidth
    const viewportHeight = window.innerHeight
    const centerX = viewportWidth / 2
    const centerY = viewportHeight / 2

    // Initialize positions and velocities for new widgets
    const velocities = new Map<string, { vx: number; vy: number }>()

    for (const widget of widgets) {
      const currentPos = positionsRef.current.get(widget.id)

      if (!currentPos) {
        // New widget: position at center with slight random offset
        const angle = Math.random() * Math.PI * 2
        const offset = 50 + Math.random() * 100
        positionsRef.current.set(widget.id, {
          x: centerX + Math.cos(angle) * offset,
          y: centerY + Math.sin(angle) * offset
        })
        velocities.set(widget.id, { vx: 0, vy: 0 })
      } else {
        velocities.set(widget.id, { vx: 0, vy: 0 })
      }
    }

    // Calculate forces for each widget
    for (const widget of widgets) {
      const pos = positionsRef.current.get(widget.id)
      if (!pos) continue

      let fx = 0
      let fy = 0

      // Repulsion from other widgets (Voronoi-style)
      for (const other of widgets) {
        if (other.id === widget.id) continue

        const otherPos = positionsRef.current.get(other.id)
        if (!otherPos) continue

        const repulsion = calculateRepulsion(
          pos.x, pos.y, widget.width, widget.height,
          otherPos.x, otherPos.y, other.width, other.height
        )
        fx += repulsion.fx
        fy += repulsion.fy
      }

      // Attraction to center
      const attraction = calculateAttraction(pos.x, pos.y, centerX, centerY)
      fx += attraction.fx
      fy += attraction.fy

      // Update velocity
      const vel = velocities.get(widget.id)
      if (vel) {
        vel.vx = (vel.vx + fx) * LAYOUT_PHYSICS.DAMPING
        vel.vy = (vel.vy + fy) * LAYOUT_PHYSICS.DAMPING
      }
    }

    // Update positions
    for (const widget of widgets) {
      const pos = positionsRef.current.get(widget.id)
      const vel = velocities.get(widget.id)

      if (pos && vel) {
        let newX = pos.x + vel.vx
        let newY = pos.y + vel.vy

        // Apply boundary constraints
        const constrained = applyBoundaryConstraints(
          newX, newY, widget.width, widget.height,
          viewportWidth, viewportHeight
        )

        positionsRef.current.set(widget.id, { x: constrained.x, y: constrained.y })
      }
    }

    // Notify parent of updated positions - only if positions actually changed
    // This prevents infinite loops when positions stabilize
    const currentPositions = positionsRef.current
    let positionsChanged = false

    // Check if any position changed since last notification
    for (const [id, pos] of currentPositions.entries()) {
      const lastPos = lastNotifiedPositionsRef.current.get(id)
      if (!lastPos || lastPos.x !== pos.x || lastPos.y !== pos.y) {
        positionsChanged = true
        break
      }
    }

    if (positionsChanged) {
      lastNotifiedPositionsRef.current = new Map(currentPositions)
      onPositionsUpdateRef.current?.(new Map(currentPositions))
    }

    // Continue animation if layout is still settling
    const maxVelocity = Array.from(velocities.values()).reduce(
      (max, vel) => Math.max(max, Math.abs(vel.vx) + Math.abs(vel.vy)),
      0
    )

    if (maxVelocity > LAYOUT_PHYSICS.SETTLING_THRESHOLD && isLayoutActiveRef.current) {
      animationFrameRef.current = requestAnimationFrame(simulateLayout)
    }
  }, [widgets])

  /**
   * Start the layout simulation when widgets change.
   * Only run on widget list length changes, not on position updates.
   */
  const widgetsLength = widgets.length
  useEffect(() => {
    isLayoutActiveRef.current = true

    // Cancel any existing animation
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }

    // Start new simulation
    animationFrameRef.current = requestAnimationFrame(simulateLayout)

    return () => {
      isLayoutActiveRef.current = false
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [widgetsLength, simulateLayout]) // Only depend on length, not full widgets array

  return <>{children}</>
}

/**
 * Hook to use Voronoi layout for widget positioning.
 *
 * This hook provides:
 * - A function to register widget positions
 * - Automatic layout calculation using Voronoi-style forces
 * - Smooth position updates via Framer Motion
 */
export function useVoronoiLayout() {
  const positionsRef = useRef<Map<string, { x: number; y: number }>>(new Map())

  const updateWidgetPositions = useCallback((widgets: Array<{
    id: string
    x: number
    y: number
    width: number
    height: number
  }>) => {
    // This would trigger the Voronoi layout calculation
    // For now, return current positions
    const result = new Map<string, { x: number; y: number }>()

    for (const widget of widgets) {
      result.set(widget.id, { x: widget.x, y: widget.y })
    }

    return result
  }, [])

  return {
    positions: positionsRef.current,
    updateWidgetPositions
  }
}
