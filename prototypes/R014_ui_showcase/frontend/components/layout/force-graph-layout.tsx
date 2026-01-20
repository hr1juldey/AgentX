"use client";

import { useEffect, useRef, useMemo } from "react";
import { forceSimulation, forceRadial, forceCollide, forceCenter, forceManyBody } from "d3-force";

interface WidgetNode {
  id: string;
  x: number;
  y: number;
  radius: number;
}

interface ForceGraphLayoutProps {
  widgets: Array<{ id: string }>;
  center: { x: number; y: number };
  islandRadius: number;
  onPositionsCalculated: (positions: Record<string, { x: number; y: number }>) => void;
}

// Helper to check if positions are approximately the same (within 1px tolerance)
function positionsEqual(
  a: Record<string, { x: number; y: number }>,
  b: Record<string, { x: number; y: number }>
): boolean {
  const keysA = Object.keys(a);
  const keysB = Object.keys(b);

  if (keysA.length !== keysB.length) return false;

  for (const key of keysA) {
    if (!b[key]) return false;
    const dx = Math.abs(a[key].x - b[key].x);
    const dy = Math.abs(a[key].y - b[key].y);
    if (dx > 1 || dy > 1) return false; // 1px tolerance
  }

  return true;
}

/**
 * ForceGraphLayout - D3 force simulation for radial positioning
 *
 * Computes island positions using D3 force simulation:
 * - Radial force: arranges widgets in circle around center
 * - Charge force: repels widgets from each other
 * - Collide force: prevents widget overlap
 * - Center force: keeps widgets centered
 *
 * Dynamic radius based on widget count:
 * - 1-4 widgets: 160px
 * - 5-8 widgets: 200px
 * - 9-12 widgets: 240px
 */
export function ForceGraphLayout({
  widgets,
  center,
  islandRadius,
  onPositionsCalculated,
}: ForceGraphLayoutProps) {
  const simulationRef = useRef<ReturnType<typeof forceSimulation<WidgetNode>> | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastPositionsRef = useRef<Record<string, { x: number; y: number }>>({});
  const isUpdatingRef = useRef(false);
  const hasCalculatedRef = useRef(false);
  const lastInputHashRef = useRef("");

  // Memoize the widget IDs to detect actual changes
  const widgetIds = useMemo(() => widgets.map((w) => w.id).join(","), [widgets]);

  // Memoize center as a string for comparison
  const centerKey = useMemo(() => `${center.x},${center.y}`, [center.x, center.y]);

  // Create a hash of the input to detect actual changes
  const inputHash = useMemo(
    () => `${widgetIds}-${centerKey}-${islandRadius}`,
    [widgetIds, centerKey, islandRadius]
  );

  // Stable callback ref
  const onPositionsCalculatedRef = useRef(onPositionsCalculated);
  useEffect(() => {
    onPositionsCalculatedRef.current = onPositionsCalculated;
  }, [onPositionsCalculated]);

  useEffect(() => {
    // If input hasn't changed and we've already calculated, skip
    if (inputHash === lastInputHashRef.current && hasCalculatedRef.current) {
      return;
    }

    // Reset calculation flag when input changes
    if (inputHash !== lastInputHashRef.current) {
      lastInputHashRef.current = inputHash;
      hasCalculatedRef.current = false;
      lastPositionsRef.current = {};
    }

    // Prevent recursive updates from our own callback
    if (isUpdatingRef.current) {
      isUpdatingRef.current = false;
      return;
    }

    if (widgets.length === 0) {
      if (Object.keys(lastPositionsRef.current).length > 0) {
        lastPositionsRef.current = {};
        isUpdatingRef.current = true;
        onPositionsCalculatedRef.current({});
      }
      return;
    }

    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Calculate dynamic radius based on widget count
    const getRadius = (count: number): number => {
      if (count <= 4) return 160;
      if (count <= 8) return 200;
      return 240;
    };

    const radius = getRadius(widgets.length);

    // Create nodes for simulation
    const nodes: WidgetNode[] = widgets.map((widget, index) => {
      // Initial position in a circle
      const angle = (index / widgets.length) * 2 * Math.PI - Math.PI / 2;
      return {
        id: widget.id,
        x: center.x + radius * Math.cos(angle),
        y: center.y + radius * Math.sin(angle),
        radius: islandRadius,
      };
    });

    // Create simulation
    const simulation = forceSimulation<WidgetNode>(nodes)
      .force(
        "radial",
        forceRadial<WidgetNode>(radius, center.x, center.y).strength(0.8)
      )
      .force("charge", forceManyBody<WidgetNode>().strength(-50))
      .force("collide", forceCollide<WidgetNode>((d) => d.radius + 8).iterations(2))
      .force("center", forceCenter<WidgetNode>(center.x, center.y).strength(0.1))
      .alphaDecay(0.05)
      .stop();

    // Run simulation
    for (let i = 0; i < 300; i++) {
      simulation.tick();
    }

    // Extract final positions
    const positions: Record<string, { x: number; y: number }> = {};
    nodes.forEach((node) => {
      positions[node.id] = { x: Math.round(node.x), y: Math.round(node.y) }; // Round to integers for stability
    });

    // Check if positions actually changed before notifying (using tolerance)
    const positionsChanged = !positionsEqual(positions, lastPositionsRef.current);
    if (positionsChanged) {
      lastPositionsRef.current = positions;
      isUpdatingRef.current = true;
      hasCalculatedRef.current = true; // Mark as calculated for this input
      onPositionsCalculatedRef.current(positions);
    } else {
      // Even if positions haven't changed, mark as calculated to prevent re-runs
      hasCalculatedRef.current = true;
    }

    // Store reference for cleanup
    simulationRef.current = simulation;

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, [widgetIds, centerKey, islandRadius]);

  // This component doesn't render anything
  return null;
}
