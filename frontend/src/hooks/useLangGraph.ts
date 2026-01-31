/**
 * LangGraph React hooks for Real AgentX v0.1.
 *
 * Custom implementation of useStream, useThread, and related hooks
 * for server-driven UI with LangGraph backend integration.
 *
 * These hooks provide:
 * - Streaming connection to LangGraph backend
 * - Thread state management (messages, UI widgets)
 * - UI message reducer integration
 * - Real-time updates from push_ui_message()
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import { Client } from '@langchain/langgraph-sdk';
import type {
  BaseMessage,
  UIMessage,
  AgentState,
} from '@/agent/graph';
import { uiMessageReducer, addMessages } from '@/agent/graph';
import type { UIComponentMessage } from '@/types/websocket';

/**
 * Generate a UUID with fallback for browsers that don't support crypto.randomUUID().
 */
function generateUUID(): string {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback: generate a random UUID v4
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Configuration for useStream hook.
 */
export interface UseStreamOptions {
  apiUrl: string;
  threadId?: string;
  onError?: (error: Error) => void;
  onCustomEvent?: (event: any, options: { mutate: (fn: (state: AgentState) => AgentState) => void }) => void;
}

/**
 * Return type for useStream hook.
 */
export interface UseStreamReturn {
  thread: { threadId: string };
  values: AgentState;
  status: 'idle' | 'streaming' | 'error';
  error: Error | null;
}

/**
 * LangGraph streaming hook - custom implementation.
 *
 * Manages streaming connection to LangGraph backend and provides:
 * - Thread state (messages, UI widgets)
 * - Real-time updates from backend
 * - UI message reducer integration
 *
 * Usage:
 * ```tsx
 * const { thread, values, status } = useStream({
 *   apiUrl: 'http://localhost:8019',
 *   threadId: 'thread-123',
 *   onCustomEvent: (event, { mutate }) => {
 *     // Handle UI messages
 *     if (event.name === 'ui_component') {
 *       mutate((state) => ({
 *         ...state,
 *         ui: uiMessageReducer(state.ui, event.args),
 *       }));
 *     }
 *   },
 * });
 * ```
 */
export function useStream(options: UseStreamOptions): UseStreamReturn {
  const { apiUrl, threadId: initialThreadId, onError, onCustomEvent } = options;

  const [threadId] = useState<string>(initialThreadId ?? generateUUID());
  const [values, setValues] = useState<AgentState>(() => ({
    messages: [],
    ui: [],
    session_id: threadId,
    reasoning_steps: 0,
    total_tool_calls: 0,
    contextualized_data: undefined,
  }));
  const [status, setStatus] = useState<'idle' | 'streaming' | 'error'>('idle');
  const [error, setError] = useState<Error | null>(null);

  const clientRef = useRef<Client | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  /**
   * Mutate function for updating state.
   */
  const mutate = useCallback((fn: (state: AgentState) => AgentState) => {
    setValues((prev) => fn(prev));
  }, []);

  /**
   * Initialize LangGraph client.
   */
  useEffect(() => {
    try {
      clientRef.current = new Client({ apiUrl });
    } catch (err) {
      setError(err as Error);
      setStatus('error');
      onError?.(err as Error);
    }
  }, [apiUrl, onError]);

  /**
   * Setup event source for streaming updates.
   */
  useEffect(() => {
    if (!clientRef.current || !threadId) return;

    const eventSource = new EventSource(`${apiUrl}/threads/${threadId}/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setStatus('streaming');
      setError(null);
    };

    eventSource.onerror = (err) => {
      console.error('EventSource error:', err);
      setStatus('error');
      setError(new Error('Stream connection failed'));
      onError?.(new Error('Stream connection failed'));
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle custom events (UI messages, etc.)
        if (data.event === 'custom' && onCustomEvent) {
          onCustomEvent(data.data, { mutate });
        }

        // Handle message updates
        if (data.event === 'messages/partial' || data.event === 'messages/complete') {
          mutate((state) => ({
            ...state,
            messages: addMessages(state.messages, data.data.messages ?? []),
          }));
        }
      } catch (err) {
        console.error('Failed to parse stream event:', err);
      }
    };

    return () => {
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [apiUrl, threadId, onCustomEvent, mutate, onError]);

  const thread = useMemo(() => ({ threadId }), [threadId]);

  return { thread, values, status, error };
}

/**
 * Configuration for useThread hook.
 */
export interface UseThreadOptions {
  apiUrl: string;
  threadId?: string;
}

/**
 * Return type for useThread hook.
 */
export interface UseThreadReturn {
  thread: { threadId: string } | null;
  state: AgentState | null;
  sendMessage: (content: string) => Promise<void>;
  createThread: () => Promise<void>;
  isLoading: boolean;
  error: Error | null;
}

/**
 * LangGraph thread hook - manages thread state and operations.
 *
 * Provides:
 * - Thread creation and management
 * - State updates (not message sending - use RunsClient for that)
 * - State querying
 */
export function useThread(options: UseThreadOptions): UseThreadReturn {
  const { apiUrl, threadId: initialThreadId } = options;

  const [threadId, setThreadId] = useState<string | undefined>(initialThreadId);
  const [state, setState] = useState<AgentState | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const clientRef = useRef<Client | null>(null);

  useEffect(() => {
    try {
      clientRef.current = new Client({ apiUrl });
    } catch (err) {
      setError(err as Error);
    }
  }, [apiUrl]);

  /**
   * Create a new thread.
   */
  const createThread = useCallback(async () => {
    if (!clientRef.current) return;

    setIsLoading(true);
    setError(null);

    try {
      const thread = await clientRef.current.threads.create({});
      setThreadId(thread.thread_id);
      setState({
        messages: [],
        ui: [],
        session_id: thread.thread_id,
        reasoning_steps: 0,
        total_tool_calls: 0,
        contextualized_data: undefined,
      });
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Send a message to the thread.
   * Note: This creates a run on the thread using the RunsClient.
   * For full streaming support, use useStream() instead.
   */
  const sendMessage = useCallback(
    async (content: string, assistantId: string = 'agent') => {
      if (!clientRef.current || !threadId) {
        setError(new Error('No thread available'));
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Create a run with the message as input
        const run = await clientRef.current.runs.create(threadId, assistantId, {
          input: { messages: [{ role: 'user', content }] },
        });

        // Refresh state after sending
        const threadState = await clientRef.current.threads.getState(threadId);
        setState(threadState.values as AgentState);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    [threadId]
  );

  const thread = useMemo(
    () => (threadId ? { threadId } : null),
    [threadId]
  );

  return {
    thread,
    state,
    sendMessage,
    createThread,
    isLoading,
    error,
  };
}

/**
 * UI state hook - manages UI widget state with reducer.
 *
 * Provides the ui field from AgentState with automatic
 * ui_message_reducer integration.
 */
export function useUIState(initialState: AgentState) {
  const [ui, setUI] = useState<UIMessage[]>(initialState.ui);

  /**
   * Add UI messages (from push_ui_message backend events).
   */
  const addUIMessages = useCallback((incoming: UIMessage | UIMessage[]) => {
    setUI((prev) => uiMessageReducer(prev, incoming));
  }, []);

  /**
   * Clear all UI widgets.
   */
  const clearUI = useCallback(() => {
    setUI([]);
  }, []);

  return { ui, addUIMessages, clearUI };
}
