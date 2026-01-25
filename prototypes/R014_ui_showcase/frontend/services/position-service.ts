// EXTRACTED from app/page.tsx (lines 638-689)
// Position calculation service for widget placement
// Handles collision detection and safe zone calculation

import type { UIDescriptor } from "@/types/widget-types";

/**
 * Position interface
 */
export interface Position {
  x: number;
  y: number;
}

/**
 * Configuration for widget position generation
 */
interface PositionConfig {
  sidebarOpen: boolean;
  viewportWidth?: number;
  viewportHeight?: number;
}

/**
 * Widget collision dimensions
 */
const WIDGET_CONFIG = {
  width: 300,
  height: 200,
  padding: 20,
} as const;

/**
 * Safe zone boundaries (in pixels)
 */
const SAFE_ZONES = {
  headerHeight: 56,
  sidebarWidth: 320,
  edgeMargin: 80,
  topMargin: 80,
  bottomMargin: 200,
} as const;

/**
 * Generate a safe position for a widget, avoiding collisions with existing widgets.
 *
 * @param id - Widget ID for deterministic positioning
 * @param existingWidgets - Array of existing widgets to avoid
 * @param config - Position configuration
 * @returns A safe position {x, y}
 *
 * Algorithm:
 * 1. Calculate safe zones respecting sidebar (320px when open)
 * 2. Use hash of widget ID for deterministic starting position
 * 3. Try up to 50 positions with increasing offsets
 * 4. Use AABB collision detection to avoid overlaps
 * 5. Fallback to hash-based position if all attempts collide
 *
 * Note: This function is used by MobileBubbleLayer for mobile positioning.
 * Desktop widgets use the Zustand store's generateSafePosition which has
 * additional logic for central island danger zone.
 */
export function generateSafePosition(
  id: string,
  existingWidgets: UIDescriptor[] = [],
  config: PositionConfig
): Position {
  const vw = config.viewportWidth ?? (typeof window !== "undefined" ? window.innerWidth : 1200);
  const vh = config.viewportHeight ?? (typeof window !== "undefined" ? window.innerHeight : 800);

  // Safe zones (respect header: 56px, sidebar: 320px when open)
  const sidebarOffset = config.sidebarOpen ? SAFE_ZONES.sidebarWidth : 0;
  const minX = sidebarOffset + SAFE_ZONES.edgeMargin;
  const maxX = vw - SAFE_ZONES.edgeMargin;
  const minY = SAFE_ZONES.topMargin;
  const maxY = vh - SAFE_ZONES.bottomMargin;

  // Use hash of ID for deterministic starting position
  const hash = id.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);

  // Try up to 50 positions to find a non-colliding spot
  for (let attempt = 0; attempt < 50; attempt++) {
    // Generate position with hash + attempt offset for determinism
    const x = ((hash + attempt * 137) % (maxX - minX - WIDGET_CONFIG.width)) + minX;
    const y = ((hash + attempt * 251) % (maxY - minY - WIDGET_CONFIG.height)) + minY;

    // Check for collisions with existing widgets
    let hasCollision = false;
    for (const widget of existingWidgets) {
      const wx = widget.x ?? (maxX / 2);
      const wy = widget.y ?? (maxY / 2);

      // Simple AABB collision detection
      const xOverlap = Math.abs(x - wx) < (WIDGET_CONFIG.width + WIDGET_CONFIG.padding);
      const yOverlap = Math.abs(y - wy) < (WIDGET_CONFIG.height + WIDGET_CONFIG.padding);

      if (xOverlap && yOverlap) {
        hasCollision = true;
        break;
      }
    }

    // Return first non-colliding position
    if (!hasCollision) {
      return { x, y };
    }
  }

  // Fallback: use hash-based position (may overlap but guaranteed to return)
  const x = (hash % (maxX - minX)) + minX;
  const y = (hash % (maxY - minY)) + minY;
  return { x, y };
}
