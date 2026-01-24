import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

// Types
export type ViewMode = 'main' | 'gallery' | 'sessions' | 'connectors'
export type ThemeMode = 'light' | 'dark' | 'system'

// State interface
interface UIState {
  // Navigation
  currentView: ViewMode
  sidebarOpen: boolean

  // Theme
  theme: ThemeMode

  // Loading states
  globalLoading: boolean
  loadingMessage: string | null

  // Central Island state
  centralIslandMode: 'idle' | 'chat' | 'voice'
  centralIslandExpanded: boolean

  // Mobile state
  isMobile: boolean
  keyboardOpen: boolean
}

// Actions interface
interface UIActions {
  // Navigation
  setCurrentView: (view: ViewMode) => void
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void

  // Theme
  setTheme: (theme: ThemeMode) => void

  // Loading
  setGlobalLoading: (loading: boolean, message?: string) => void

  // Central Island
  setCentralIslandMode: (mode: 'idle' | 'chat' | 'voice') => void
  setCentralIslandExpanded: (expanded: boolean) => void

  // Mobile
  setIsMobile: (isMobile: boolean) => void
  setKeyboardOpen: (open: boolean) => void
}

// Combined store type
type UIStore = UIState & UIActions

// Create store with Immer middleware
export const useUIStore = create<UIStore>()(
  immer((set) => ({
    // Initial state
    currentView: 'main',
    sidebarOpen: false,
    theme: 'system',
    globalLoading: false,
    loadingMessage: null,
    centralIslandMode: 'idle',
    centralIslandExpanded: false,
    isMobile: false,
    keyboardOpen: false,

    // Navigation actions
    setCurrentView: (view) => set({ currentView: view }),
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    setSidebarOpen: (open) => set({ sidebarOpen: open }),

    // Theme
    setTheme: (theme) => set({ theme }),

    // Loading
    setGlobalLoading: (loading, message) =>
      set({ globalLoading: loading, loadingMessage: message || null }),

    // Central Island
    setCentralIslandMode: (mode) => set({ centralIslandMode: mode }),
    setCentralIslandExpanded: (expanded) => set({ centralIslandExpanded: expanded }),

    // Mobile
    setIsMobile: (isMobile) => set({ isMobile }),
    setKeyboardOpen: (open) => set({ keyboardOpen: open }),
  }))
)
