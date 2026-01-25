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

// ATOMIC STATE PATTERN (Fixes cascade re-render issue)
//
// PROBLEM: Storing widgets as Record<string, UIDescriptor> causes ALL widgets to re-render
// when ANY widget is added/deleted, because Immer creates a new parent object reference.
//
// SOLUTION: Store each widget's data as separate top-level state slices.
// When widget A is deleted, only widget A's slices are deleted - widget B's slices remain
// with the same object reference, so Zustand doesn't notify widget B's subscribers.
//
// State structure:
//   widget_{id}_data: UIDescriptor
//   widget_{id}_viewState: ViewState
//   widget_{id}_position: Position
//
// This is how Jira/Linear/Asana achieve efficient card-based UIs with hundreds of items.

// Helper to create widget slice keys
const widgetKeys = {
  data: (id: string) => `widget_${id}_data` as const,
  viewState: (id: string) => `widget_${id}_viewState` as const,
  position: (id: string) => `widget_${id}_position` as const,
}

// Base state interface - extends with widget slices dynamically
interface WidgetState {
  // Registry of all widget IDs (for iteration)
  widgetIds: string[]
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

// Options for adding widgets
interface AddWidgetOptions {
  position?: Position
  sidebarOpen?: boolean  // Pass true if sidebar is open to avoid spawning under it
}

// Combined store type - dynamic slices added via index signature
// Use a more flexible index signature that works with function types
type WidgetStore = WidgetState & WidgetActions & {
  [key: string]: unknown
}

// Position generation helper
// Generates safe positions avoiding:
// - Sidebar (320px on the left when open)
// - Central island/chat bubble (bottom-center ~400px wide, ~200px tall)
// - Other widgets
function generateSafePosition(
  id: string,
  existingWidgetIds: string[],
  getPosition: (id: string) => Position | undefined,
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

  // Build existing positions map
  const existingPositions: Record<string, Position> = {}
  existingWidgetIds.forEach(id => {
    const pos = getPosition(id)
    if (pos) existingPositions[id] = pos
  })

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

// Helper to get widget data from atomic state slices
export function getWidgetData(state: WidgetStore, id: string): {
  data: UIDescriptor | undefined
  viewState: ViewState | undefined
  position: Position | undefined
} {
  const dataKey = widgetKeys.data(id)
  const viewStateKey = widgetKeys.viewState(id)
  const positionKey = widgetKeys.position(id)

  return {
    data: state[dataKey] as UIDescriptor | undefined,
    viewState: state[viewStateKey] as ViewState | undefined,
    position: state[positionKey] as Position | undefined,
  }
}

// Helper to get all widgets as an array (for iteration)
// This returns a stable reference when widgetIds doesn't change
export function getWidgetsArray(state: WidgetStore): UIDescriptor[] {
  return state.widgetIds.map(id => state[widgetKeys.data(id)] as UIDescriptor)
}

// Create store with Immer middleware
export const useWidgetStore = create<WidgetStore>()(
  immer((set, get) => ({
    // Initial state
    widgetIds: [],

    // Add single widget
    addWidget: (descriptor, options) =>
      set((state) => {
        const safePosition = options?.position || generateSafePosition(
          descriptor.descriptor_id,
          state.widgetIds,
          (id) => state[widgetKeys.position(id)] as Position | undefined,
          options?.sidebarOpen || false
        )

        // Create atomic slices for this widget
        state[widgetKeys.data(descriptor.descriptor_id)] = descriptor
        state[widgetKeys.viewState(descriptor.descriptor_id)] = 'island'
        state[widgetKeys.position(descriptor.descriptor_id)] = safePosition

        // Add to registry if not already present
        if (!state.widgetIds.includes(descriptor.descriptor_id)) {
          state.widgetIds.push(descriptor.descriptor_id)
        }
      }),

    // Remove widget - ONLY deletes this widget's slices, leaving others untouched
    removeWidget: (id) =>
      set((state) => {
        // DIAGNOSTIC: Log widget removal to trace reference changes
        console.log(`[WidgetStore.removeWidget] Removing widget: ${id}`);
        console.log(`[WidgetStore.removeWidget] Before deletion, widgetIds:`, state.widgetIds);

        // Capture references to all widget data BEFORE deletion
        const beforeSnapshot: Record<string, unknown> = {};
        state.widgetIds.forEach(wid => {
          beforeSnapshot[`widget_${wid}_data`] = state[widgetKeys.data(wid)];
        });
        console.log(`[WidgetStore.removeWidget] Widget data references BEFORE:`, beforeSnapshot);

        // Delete only this widget's atomic slices
        delete state[widgetKeys.data(id)]
        delete state[widgetKeys.viewState(id)]
        delete state[widgetKeys.position(id)]

        // Remove from registry
        state.widgetIds = state.widgetIds.filter(widgetId => widgetId !== id)

        // Capture references to all widget data AFTER deletion
        const afterSnapshot: Record<string, unknown> = {};
        state.widgetIds.forEach(wid => {
          afterSnapshot[`widget_${wid}_data`] = state[widgetKeys.data(wid)];
        });
        console.log(`[WidgetStore.removeWidget] Widget data references AFTER:`, afterSnapshot);

        // Compare to see which references changed
        const changedIds: string[] = [];
        state.widgetIds.forEach(wid => {
          const before = beforeSnapshot[`widget_${wid}_data`];
          const after = afterSnapshot[`widget_${wid}_data`];
          if (before !== after) {
            changedIds.push(wid);
          }
        });
        console.log(`[WidgetStore.removeWidget] Widget IDs with changed references:`, changedIds);
        console.log(`[WidgetStore.removeWidget] After deletion, widgetIds:`, state.widgetIds);
      }),

    // Set view state directly
    setViewState: (id, viewState) =>
      set((state) => {
        state[widgetKeys.viewState(id)] = viewState
      }),

    // Cycle view state (island → card → full → island)
    cycleViewState: (id) =>
      set((state) => {
        const current = state[widgetKeys.viewState(id)] as ViewState || 'island'
        const cycle: Record<string, ViewState> = {
          island: 'card',
          card: 'full',
          full: 'island',
        }
        state[widgetKeys.viewState(id)] = cycle[current]
      }),

    // Update position to absolute coordinates
    updatePosition: (id, position) =>
      set((state) => {
        state[widgetKeys.position(id)] = position
      }),

    // Update position by delta (relative movement)
    updatePositionDelta: (id, dx, dy) =>
      set((state) => {
        const current = state[widgetKeys.position(id)] as Position | undefined
        if (current) {
          state[widgetKeys.position(id)] = { x: current.x + dx, y: current.y + dy }
        }
      }),

    // Add multiple widgets at once
    addWidgets: (descriptors, options) =>
      set((state) => {
        const sidebarOpen = options?.sidebarOpen || false
        descriptors.forEach((d) => {
          const safePosition = generateSafePosition(
            d.descriptor_id,
            state.widgetIds,
            (id) => state[widgetKeys.position(id)] as Position | undefined,
            sidebarOpen
          )

          state[widgetKeys.data(d.descriptor_id)] = d
          state[widgetKeys.viewState(d.descriptor_id)] = 'island'
          state[widgetKeys.position(d.descriptor_id)] = safePosition

          if (!state.widgetIds.includes(d.descriptor_id)) {
            state.widgetIds.push(d.descriptor_id)
          }
        })
      }),

    // Clear all widgets
    clearAll: () =>
      set((state) => {
        // Delete all widget slices
        state.widgetIds.forEach(id => {
          delete state[widgetKeys.data(id)]
          delete state[widgetKeys.viewState(id)]
          delete state[widgetKeys.position(id)]
        })
        state.widgetIds = []
      }),
  }))
)
