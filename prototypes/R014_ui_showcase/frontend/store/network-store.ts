import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'

// Types
export type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error'

// Session interface
export interface Session {
  id?: string
  session_id?: string
  name?: string
  title?: string
  created?: string
  created_at?: string
  date?: string
}

// QA Progress interface
export interface QACheckpoint {
  status: 'running' | 'passed' | 'failed'
  checkpoint: string
  details: Record<string, unknown>
}

// State interface
interface NetworkState {
  // WebSocket connection
  wsConnection: WebSocket | null
  wsStatus: ConnectionStatus
  wsUrl: string

  // Reconnection
  reconnectAttempts: number
  maxReconnectAttempts: number
  reconnectDelay: number

  // API state
  apiHealth: 'unknown' | 'healthy' | 'unhealthy' | 'disconnected'
  lastHealthCheck: number | null

  // Connectors state
  connectors: {
    searxng: boolean
    mem0: boolean
    qdrant: boolean
  }

  // Sessions
  sessions: Session[]

  // QA progress
  qaProgress: Record<string, QACheckpoint>

  // Streaming state
  isStreaming: boolean
  streamedMessages: string[]

  // Error handling
  lastError: string | null
  errorCount: number
}

// Actions interface
interface NetworkActions {
  // WebSocket
  setWsConnection: (ws: WebSocket | null) => void
  setWsStatus: (status: ConnectionStatus) => void
  setWsUrl: (url: string) => void

  // Reconnection
  incrementReconnectAttempts: () => void
  resetReconnectAttempts: () => void

  // API health
  setApiHealth: (health: 'unknown' | 'healthy' | 'unhealthy' | 'disconnected') => void

  // Connectors
  setConnector: (name: keyof NetworkState['connectors'], status: boolean) => void

  // Sessions
  setSessions: (sessions: Session[]) => void

  // QA progress
  setQaProgress: (checkpoint: string, status: 'running' | 'passed' | 'failed', details?: Record<string, unknown>) => void
  resetQaProgress: () => void

  // Streaming
  setIsStreaming: (streaming: boolean) => void
  addStreamedMessage: (message: string) => void
  clearStreamedMessages: () => void

  // Errors
  setError: (error: string | null) => void
  incrementErrorCount: () => void
  resetErrorCount: () => void

  // Reset
  reset: () => void
}

// Combined store type
type NetworkStore = NetworkState & NetworkActions

// Create store with Immer middleware
export const useNetworkStore = create<NetworkStore>()(
  immer((set) => ({
    // Initial state
    wsConnection: null,
    wsStatus: 'disconnected',
    wsUrl: '',
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    apiHealth: 'unknown',
    lastHealthCheck: null,
    connectors: {
      searxng: false,
      mem0: false,
      qdrant: false,
    },
    sessions: [],
    qaProgress: {},
    isStreaming: false,
    streamedMessages: [],
    lastError: null,
    errorCount: 0,

    // WebSocket
    setWsConnection: (ws) => set({ wsConnection: ws }),
    setWsStatus: (status) => set({ wsStatus: status }),
    setWsUrl: (url) => set({ wsUrl: url }),

    // Reconnection
    incrementReconnectAttempts: () => set((state) => ({ reconnectAttempts: state.reconnectAttempts + 1 })),
    resetReconnectAttempts: () => set({ reconnectAttempts: 0 }),

    // API health
    setApiHealth: (health) => set({
      apiHealth: health,
      lastHealthCheck: Date.now()
    }),

    // Connectors
    setConnector: (name, status) => set((state) => ({
      connectors: { ...state.connectors, [name]: status }
    })),

    // Sessions
    setSessions: (sessions) => set({ sessions }),

    // QA progress
    setQaProgress: (checkpoint, status, details = {}) => set((state) => ({
      qaProgress: {
        ...state.qaProgress,
        [checkpoint]: { status, checkpoint, details }
      }
    })),

    resetQaProgress: () => set({ qaProgress: {} }),

    // Streaming
    setIsStreaming: (streaming) => set({ isStreaming: streaming }),
    addStreamedMessage: (message) => set((state) => ({
      streamedMessages: [...state.streamedMessages, message]
    })),
    clearStreamedMessages: () => set({ streamedMessages: [] }),

    // Errors
    setError: (error) => set({ lastError: error }),
    incrementErrorCount: () => set((state) => ({ errorCount: state.errorCount + 1 })),
    resetErrorCount: () => set({ errorCount: 0 }),

    // Reset
    reset: () => set({
      wsConnection: null,
      wsStatus: 'disconnected',
      reconnectAttempts: 0,
      lastError: null,
      streamedMessages: [],
      isStreaming: false,
    }),
  }))
)
