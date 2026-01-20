"use client"

import { useEffect, useRef, useCallback } from "react"
import { motion, useMotionValue } from "framer-motion"

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

  // Physics parameters for the force-directed layout
  const REPULSION_STRENGTH = 5000  // Strength of widget-to-widget repulsion
  const ATTRACTION_STRENGTH = 0.01 // Strength of center attraction
  const DAMPING = 0.85              // Velocity damping (0-1)
  const MIN_DISTANCE = 50          // Minimum distance between widgets
  const WIDGET_PADDING = 20         // Padding around each widget

  /**
   * Calculate the repulsive force between two widgets.
   * Uses inverse-square law (like electrostatic force).
   */
  const calculateRepulsion = useCallback((
    x1: number, y1: number, w1: number, h1: number,
    x2: number, y2: number, w2: number, h2: number
  ) => {
    const dx = x1 - x2
    const dy = y1 - y2
    const distance = Math.sqrt(dx * dx + dy * dy)

    // Prevent division by zero and limit minimum distance
    const effectiveDistance = Math.max(distance, MIN_DISTANCE)

    // Calculate combined size for collision detection
    const minRequiredDist = (Math.max(w1, w2) + Math.max(h1, h2)) / 2 + WIDGET_PADDING

    // If widgets overlap, apply stronger repulsion
    const strength = distance < minRequiredDist
      ? REPULSION_STRENGTH * 3
      : REPULSION_STRENGTH

    // Inverse-square law: F = k / r^2
    const force = strength / (effectiveDistance * effectiveDistance)

    return {
      fx: (dx / distance) * force,
      fy: (dy / distance) * force
    }
  }, [])

  /**
   * Calculate the attractive force toward the center of the screen.
   * This keeps widgets from drifting off-screen.
   */
  const calculateAttraction = useCallback((x: number, y: number, centerX: number, centerY: number) => {
    return {
      fx: (centerX - x) * ATTRACTION_STRENGTH,
      fy: (centerY - y) * ATTRACTION_STRENGTH
    }
  }, [])

  /**
   * Apply boundary constraints to keep widgets within viewport.
   */
  const applyBoundaryConstraints = useCallback((
    x: number, y: number, width: number, height: number,
    viewportWidth: number, viewportHeight: number
  ) => {
    const margin = 50
    return {
      x: Math.max(margin, Math.min(viewportWidth - width - margin, x)),
      y: Math.max(margin, Math.min(viewportHeight - height - margin, y))
    }
  }, [])

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
        vel.vx = (vel.vx + fx) * DAMPING
        vel.vy = (vel.vy + fy) * DAMPING
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

    if (maxVelocity > 0.1 && isLayoutActiveRef.current) {
      animationFrameRef.current = requestAnimationFrame(simulateLayout)
    }
  }, [widgets, calculateRepulsion, calculateAttraction, applyBoundaryConstraints])

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
