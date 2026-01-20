/**
 * Collision Resolver - Iterative collision detection for expanded panels
 *
 * Algorithm inspired by GraphRAG visualizations:
 * - Iterative approach (5 iterations)
 * - Bidirectional push algorithm
 * - Computes push vectors for overlapping panels
 * - Handles multiple simultaneous collisions
 */

export interface Vector2D {
  x: number;
  y: number;
}

export interface PanelBounds {
  id: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface PushVector {
  x: number;
  y: number;
}

const DEFAULT_PANEL_WIDTH = 420;
const DEFAULT_PANEL_HEIGHT = 300;
const MIN_OVERLAP = 1; // Minimum overlap in pixels to trigger push
const PUSH_STRENGTH = 0.6; // How much to push per iteration
const ITERATIONS = 5; // Number of solver iterations

/**
 * Check if two panels overlap
 */
function isOverlapping(a: PanelBounds, b: PanelBounds): boolean {
  const aLeft = a.x - a.width / 2;
  const aRight = a.x + a.width / 2;
  const aTop = a.y - a.height / 2;
  const aBottom = a.y + a.height / 2;

  const bLeft = b.x - b.width / 2;
  const bRight = b.x + b.width / 2;
  const bTop = b.y - b.height / 2;
  const bBottom = b.y + b.height / 2;

  return !(aRight < bLeft || aLeft > bRight || aBottom < bTop || aTop > bBottom);
}

/**
 * Calculate overlap area between two panels
 */
function calculateOverlap(a: PanelBounds, b: PanelBounds): Vector2D {
  const aLeft = a.x - a.width / 2;
  const aRight = a.x + a.width / 2;
  const aTop = a.y - a.height / 2;
  const aBottom = a.y + a.height / 2;

  const bLeft = b.x - b.width / 2;
  const bRight = b.x + b.width / 2;
  const bTop = b.y - b.height / 2;
  const bBottom = b.y + b.height / 2;

  const overlapX = Math.min(aRight, bRight) - Math.max(aLeft, bLeft);
  const overlapY = Math.min(aBottom, bBottom) - Math.max(aTop, bTop);

  return { x: overlapX, y: overlapY };
}

/**
 * Compute bidirectional push vector for two overlapping panels
 *
 * Push direction is from panel A's center to panel B's center
 * Push magnitude is proportional to overlap amount
 */
function computeBidirectionalPush(a: PanelBounds, b: PanelBounds): Vector2D {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  if (distance === 0) {
    // Panels are at the same position, push apart randomly
    return { x: Math.random() - 0.5, y: Math.random() - 0.5 };
  }

  const overlap = calculateOverlap(a, b);

  // Normalize direction
  const nx = dx / distance;
  const ny = dy / distance;

  // Calculate push magnitude based on overlap
  const pushMagnitude = Math.max(overlap.x, overlap.y) * PUSH_STRENGTH;

  return {
    x: nx * pushMagnitude,
    y: ny * pushMagnitude,
  };
}

/**
 * Resolve collisions between multiple panels
 *
 * @param panels - Array of panel bounds with positions
 * @returns Record mapping panel IDs to their push vectors
 */
export function resolveCollisions(
  panels: PanelBounds[]
): Record<string, PushVector> {
  if (panels.length === 0) {
    return {};
  }

  // Initialize push vectors for each panel
  const pushVectors: Record<string, PushVector> = {};
  panels.forEach((panel) => {
    pushVectors[panel.id] = { x: 0, y: 0 };
  });

  // Iterative collision resolution
  for (let i = 0; i < ITERATIONS; i++) {
    for (let a = 0; a < panels.length; a++) {
      for (let b = a + 1; b < panels.length; b++) {
        const panelA = panels[a];
        const panelB = panels[b];

        if (isOverlapping(panelA, panelB)) {
          const overlap = calculateOverlap(panelA, panelB);

          // Only push if there's significant overlap
          if (overlap.x > MIN_OVERLAP || overlap.y > MIN_OVERLAP) {
            const push = computeBidirectionalPush(panelA, panelB);

            // Apply bidirectional push
            pushVectors[panelA.id].x -= push.x;
            pushVectors[panelA.id].y -= push.y;
            pushVectors[panelB.id].x += push.x;
            pushVectors[panelB.id].y += push.y;
          }
        }
      }
    }
  }

  return pushVectors;
}

/**
 * Create panel bounds from position and optional dimensions
 */
export function createPanelBounds(
  id: string,
  position: { x: number; y: number },
  width: number = DEFAULT_PANEL_WIDTH,
  height: number = DEFAULT_PANEL_HEIGHT
): PanelBounds {
  return {
    id,
    x: position.x,
    y: position.y,
    width,
    height,
  };
}
