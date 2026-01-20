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

  // Memoize the widget IDs to detect actual changes
  const widgetIds = useMemo(() => widgets.map((w) => w.id).join(","), [widgets]);

  // Memoize center as a string for comparison
  const centerKey = useMemo(() => `${center.x},${center.y}`, [center.x, center.y]);

  useEffect(() => {
    if (widgets.length === 0) {
      if (Object.keys(lastPositionsRef.current).length > 0) {
        lastPositionsRef.current = {};
        onPositionsCalculated({});
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

    // Run simulation for ~3 seconds (180 ticks at 60fps)
    for (let i = 0; i < 180; i++) {
      simulation.tick();
    }

    // Extract final positions
    const positions: Record<string, { x: number; y: number }> = {};
    nodes.forEach((node) => {
      positions[node.id] = { x: node.x, y: node.y };
    });

    // Check if positions actually changed before notifying
    const positionsChanged = JSON.stringify(positions) !== JSON.stringify(lastPositionsRef.current);
    if (positionsChanged) {
      lastPositionsRef.current = positions;
      onPositionsCalculated(positions);
    }

    // Store reference for cleanup
    simulationRef.current = simulation;

    // Set up a delayed update for smooth animation
    timeoutRef.current = setTimeout(() => {
      // Optional: trigger a second pass for fine-tuning
      for (let i = 0; i < 60; i++) {
        simulation.tick();
      }

      const finalPositions: Record<string, { x: number; y: number }> = {};
      nodes.forEach((node) => {
        finalPositions[node.id] = { x: node.x, y: node.y };
      });

      // Check if final positions changed
      const finalChanged = JSON.stringify(finalPositions) !== JSON.stringify(lastPositionsRef.current);
      if (finalChanged) {
        lastPositionsRef.current = finalPositions;
        onPositionsCalculated(finalPositions);
      }
    }, 100);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (simulationRef.current) {
        simulationRef.current.stop();
      }
    };
  }, [widgetIds, centerKey, islandRadius, onPositionsCalculated]);

  // This component doesn't render anything
  return null;
}
