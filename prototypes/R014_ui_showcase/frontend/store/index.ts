// Export all stores for easy importing
export { useWidgetStore } from './widget-store'

// UI Store (Phase 1)
export { useUIStore } from './ui-store'

// Network Store (Phase 1)
export { useNetworkStore } from './network-store'

// Re-export types for convenience
export type { ViewState, Position, UIDescriptor } from './widget-store'
export type { ViewMode, ThemeMode } from './ui-store'
