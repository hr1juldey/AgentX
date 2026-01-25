import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

// Types
export type ViewState = 'island' | 'card' | 'full'

export interface Position {
  x: number
  y: number
}

// Reusing UIDescriptor interface from existing code
export interface UIDescriptor {
  descriptor_id: string
  descriptor_type: string
  title?: string
  x?: number
  y?: number
  collapsed?: boolean
  metadata?: Record<string, unknown>
  content?: string
  fields?: Array<{
    name: string
    type: string
    label: string
    required: boolean
    options?: string[]
  }>
  button_text?: string
  message?: string
  confirm_label?: string
  cancel_label?: string
  submit_button_text?: string
  citations?: Array<Record<string, unknown>>
  hop_events?: Array<Record<string, unknown>>
  id?: string
}

// State interface
// Using plain objects instead of Maps for proper Zustand change tracking
// Maps cause all components to re-render on any change because Zustand
// cannot track which specific key was accessed
interface WidgetState {
  // Objects for granular change tracking - only components accessing
  // specific widget IDs will re-render when that widget changes
  widgets: Record<string, UIDescriptor>
  viewStates: Record<string, ViewState>
  positions: Record<string, Position>
}

// Options for adding widgets
interface AddWidgetOptions {
  position?: Position
  sidebarOpen?: boolean  // Pass true if sidebar is open to avoid spawning under it
}

// Actions interface
interface WidgetActions {
  // CRUD operations
  addWidget: (descriptor: UIDescriptor, options?: AddWidgetOptions) => void
  removeWidget: (id: string) => void

  // State management
  setViewState: (id: string, state: ViewState) => void
  cycleViewState: (id: string) => void

  // Position management
  updatePosition: (id: string, position: Position) => void
  updatePositionDelta: (id: string, dx: number, dy: number) => void

  // Batch operations
  addWidgets: (descriptors: UIDescriptor[], options?: AddWidgetOptions) => void
  clearAll: () => void
}

// Combined store type
type WidgetStore = WidgetState & WidgetActions

// Position generation helper
// Generates safe positions avoiding:
// - Sidebar (320px on the left when open)
// - Central island/chat bubble (bottom-center ~400px wide, ~200px tall)
// - Other widgets
function generateSafePosition(
  id: string,
  existingPositions: Record<string, Position>,
  sidebarOpen = false
): Position {
  const vw = typeof window !== 'undefined' ? window.innerWidth : 1200
  const vh = typeof window !== 'undefined' ? window.innerHeight : 800

  // Use hash of ID for deterministic position
  const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)

  // Widget dimensions
  const widgetWidth = 300
  const widgetHeight = 200
  const padding = 20

  // Safe zones - account for sidebar and ensure widget stays on screen
  const sidebarOffset = sidebarOpen ? 320 : 0
  const minX = sidebarOffset + 80
  const maxX = Math.max(minX + widgetWidth, vw - 80)  // Ensure maxX > minX
  const availableWidth = maxX - minX - widgetWidth

  const minY = 80
  const maxY = Math.max(minY + widgetHeight, vh - 280)  // Ensure maxY > minY
  const availableHeight = maxY - minY - widgetHeight

  // Central island "danger zone" - avoid spawning in bottom-center area
  const centerX = vw / 2
  const dangerZoneWidth = 450
  const dangerZoneMinX = centerX - dangerZoneWidth / 2
  const dangerZoneMaxX = centerX + dangerZoneWidth / 2

  // Helper function to clamp value to range
  const clamp = (val: number, min: number, max: number) => Math.min(Math.max(val, min), max)

  // Try up to 50 positions to find a safe spot
  for (let attempt = 0; attempt < 50; attempt++) {
    // Generate position using hash + attempt for deterministic spread
    const hashOffset = hash + attempt * 137
    const x = minX + (hashOffset % Math.max(1, availableWidth))
    const y = minY + ((hashOffset * 251) % Math.max(1, availableHeight))

    // Clamp to bounds
    const testX = clamp(x, minX, maxX - widgetWidth)
    const testY = clamp(y, minY, maxY - widgetHeight)

    // Check if we're in the central island danger zone (bottom-center)
    const inDangerZone = (
      testX < dangerZoneMaxX &&
      testX + widgetWidth > dangerZoneMinX &&
      testY > vh - 320  // Bottom 320px is the danger zone vertically
    )

    // Check collision with existing widgets
    const hasCollision = Object.values(existingPositions).some(
      pos => Math.abs(pos.x - testX) < (widgetWidth + padding) &&
             Math.abs(pos.y - testY) < (widgetHeight + padding)
    )

    if (!inDangerZone && !hasCollision) {
      return { x: testX, y: testY }
    }
  }

  // Fallback: guaranteed safe position within bounds (top-left corner of safe area)
  return {
    x: clamp(minX + (hash % Math.max(1, availableWidth / 2)), minX, maxX - widgetWidth),
    y: clamp(minY + ((hash * 251) % Math.max(1, availableHeight / 2)), minY, maxY - widgetHeight)
  }
}

// Create store with Immer middleware
export const useWidgetStore = create<WidgetStore>()(
  immer((set, get) => ({
    // Initial state - using plain objects for granular Zustand tracking
    widgets: {},
    viewStates: {},
    positions: {},

    // Add single widget
    addWidget: (descriptor, options) =>
      set((state) => {
        const safePosition = options?.position || generateSafePosition(
          descriptor.descriptor_id,
          state.positions,
          options?.sidebarOpen || false
        )
        state.widgets[descriptor.descriptor_id] = descriptor
        state.viewStates[descriptor.descriptor_id] = 'island'
        state.positions[descriptor.descriptor_id] = safePosition
      }),

    // Remove widget
    removeWidget: (id) =>
      set((state) => {
        delete state.widgets[id]
        delete state.viewStates[id]
        delete state.positions[id]
      }),

    // Set view state directly
    setViewState: (id, viewState) =>
      set((state) => {
        state.viewStates[id] = viewState
      }),

    // Cycle view state (island → card → full → island)
    cycleViewState: (id) =>
      set((state) => {
        const current = state.viewStates[id] || 'island'
        const cycle: Record<string, ViewState> = {
          island: 'card',
          card: 'full',
          full: 'island',
        }
        state.viewStates[id] = cycle[current]
      }),

    // Update position to absolute coordinates
    updatePosition: (id, position) =>
      set((state) => {
        state.positions[id] = position
      }),

    // Update position by delta (relative movement)
    updatePositionDelta: (id, dx, dy) =>
      set((state) => {
        const current = state.positions[id]
        if (current) {
          state.positions[id] = { x: current.x + dx, y: current.y + dy }
        }
      }),

    // Add multiple widgets at once
    addWidgets: (descriptors, options) =>
      set((state) => {
        const sidebarOpen = options?.sidebarOpen || false
        descriptors.forEach((d) => {
          const safePosition = generateSafePosition(d.descriptor_id, state.positions, sidebarOpen)
          state.widgets[d.descriptor_id] = d
          state.viewStates[d.descriptor_id] = 'island'
          state.positions[d.descriptor_id] = safePosition
        })
      }),

    // Clear all widgets
    clearAll: () =>
      set((state) => {
        state.widgets = {}
        state.viewStates = {}
        state.positions = {}
      }),
  }))
)
