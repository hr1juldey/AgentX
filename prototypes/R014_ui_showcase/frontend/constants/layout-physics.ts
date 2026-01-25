/**
 * Physics parameters for Voronoi force-directed layout algorithm
 *
 * These constants control the behavior of the collision detection and
 * layout system that spreads widgets evenly across the screen.
 */
export const LAYOUT_PHYSICS = {
  /**
   * Strength of widget-to-widget repulsion force
   * Higher values push widgets further apart
   */
  REPULSION_STRENGTH: 5000,

  /**
   * Strength of center attraction force
   * Keeps widgets from drifting off-screen
   */
  ATTRACTION_STRENGTH: 0.01,

  /**
   * Velocity damping factor (0-1)
   * Prevents infinite oscillation
   * Lower values = more damping (stops faster)
   * Higher values = less damping (continues longer)
   */
  DAMPING: 0.85,

  /**
   * Minimum distance between widget centers for force calculation
   * Prevents division by zero and extreme forces
   */
  MIN_DISTANCE: 50,

  /**
   * Padding around each widget for collision detection
   * Ensures widgets don't touch edge-to-edge
   */
  WIDGET_PADDING: 20,

  /**
   * Margin from viewport edges
   * Keeps widgets from going off-screen
   */
  VIEWPORT_MARGIN: 50,

  /**
   * Minimum velocity threshold to continue animation
   * Below this value, the layout is considered "settled"
   */
  SETTLING_THRESHOLD: 0.1,
} as const;

/**
 * Default widget dimensions for layout calculation
 * Used when actual widget dimensions are not available
 */
export const DEFAULT_WIDGET_SIZE = {
  width: 300,
  height: 200,
} as const;
