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
interface WidgetState {
  // Maps for O(1) lookups by ID
  widgets: Map<string, UIDescriptor>
  viewStates: Map<string, ViewState>
  positions: Map<string, Position>

  // Derived selector (computed when accessed)
  widgetIds: string[]
}

// Actions interface
interface WidgetActions {
  // CRUD operations
  addWidget: (descriptor: UIDescriptor, position?: Position) => void
  removeWidget: (id: string) => void

  // State management
  setViewState: (id: string, state: ViewState) => void
  cycleViewState: (id: string) => void

  // Position management
  updatePosition: (id: string, position: Position) => void
  updatePositionDelta: (id: string, dx: number, dy: number) => void

  // Batch operations
  addWidgets: (descriptors: UIDescriptor[]) => void
  clearAll: () => void
}

// Combined store type
type WidgetStore = WidgetState & WidgetActions

// Position generation helper
function generateSafePosition(id: string, existingPositions: Map<string, Position>): Position {
  const vw = typeof window !== 'undefined' ? window.innerWidth : 1200
  const vh = typeof window !== 'undefined' ? window.innerHeight : 800

  // Use hash of ID for deterministic position
  const hash = id.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0)

  // Safe zones
  const minX = 80
  const maxX = vw - 80
  const minY = 80
  const maxY = vh - 200

  let x = (hash % (maxX - minX)) + minX
  let y = (hash % (maxY - minY)) + minY

  // Avoid collision with existing positions
  let attempts = 0
  const OFFSET = 40

  while (attempts < 10) {
    const hasCollision = Array.from(existingPositions.values()).some(
      pos => Math.abs(pos.x - x) < OFFSET && Math.abs(pos.y - y) < OFFSET
    )

    if (!hasCollision) break

    // Shift position and retry
    x = (x + OFFSET) % maxX
    y = (y + OFFSET) % maxY
    attempts++
  }

  return { x, y }
}

// Create store with Immer middleware
export const useWidgetStore = create<WidgetStore>()(
  immer((set, get) => ({
    // Initial state
    widgets: new Map(),
    viewStates: new Map(),
    positions: new Map(),

    // Computed getter for widget IDs
    get widgetIds() {
      return Array.from(get().widgets.keys())
    },

    // Add single widget
    addWidget: (descriptor, position) =>
      set((state) => {
        const safePosition = position || generateSafePosition(descriptor.descriptor_id, state.positions)
        state.widgets.set(descriptor.descriptor_id, descriptor)
        state.viewStates.set(descriptor.descriptor_id, 'island')
        state.positions.set(descriptor.descriptor_id, safePosition)
      }),

    // Remove widget
    removeWidget: (id) =>
      set((state) => {
        state.widgets.delete(id)
        state.viewStates.delete(id)
        state.positions.delete(id)
      }),

    // Set view state directly
    setViewState: (id, viewState) =>
      set((state) => {
        state.viewStates.set(id, viewState)
      }),

    // Cycle view state (island → card → full → island)
    cycleViewState: (id) =>
      set((state) => {
        const current = state.viewStates.get(id) || 'island'
        const cycle: Record<string, ViewState> = {
          island: 'card',
          card: 'full',
          full: 'island',
        }
        state.viewStates.set(id, cycle[current])
      }),

    // Update position to absolute coordinates
    updatePosition: (id, position) =>
      set((state) => {
        state.positions.set(id, position)
      }),

    // Update position by delta (relative movement)
    updatePositionDelta: (id, dx, dy) =>
      set((state) => {
        const current = state.positions.get(id)
        if (current) {
          state.positions.set(id, { x: current.x + dx, y: current.y + dy })
        }
      }),

    // Add multiple widgets at once
    addWidgets: (descriptors) =>
      set((state) => {
        descriptors.forEach((d) => {
          const safePosition = generateSafePosition(d.descriptor_id, state.positions)
          state.widgets.set(d.descriptor_id, d)
          state.viewStates.set(d.descriptor_id, 'island')
          state.positions.set(d.descriptor_id, safePosition)
        })
      }),

    // Clear all widgets
    clearAll: () =>
      set((state) => {
        state.widgets.clear()
        state.viewStates.clear()
        state.positions.clear()
      }),
  }))
)
