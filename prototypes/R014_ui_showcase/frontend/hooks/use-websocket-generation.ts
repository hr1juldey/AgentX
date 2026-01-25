import { useCallback } from "react";
import { API_CONFIG } from "@/constants/widget-constants";
import type { QACheckpointStatus } from "@/types/widget-types";

interface WebSocketHandlers {
  updateQACheckpoint: (checkpoint: string, status: QACheckpointStatus, details: Record<string, unknown>) => void;
  handleWidgetMessage: (data: unknown) => void;
  handleCompleteMessage: (data: unknown) => void;
  setLoading: (loading: boolean) => void;
  setWsConnection: (ws: WebSocket | null) => void;
  handleResetQAProgress: () => void;
  setGenerationComplete: (complete: boolean) => void;
}

/**
 * Hook for WebSocket-based content generation
 * Manages WebSocket connection and message routing
 *
 * @param handlers - Callback functions for WebSocket events
 * @returns Object containing WebSocket functions
 */
export function useWebSocketGeneration(handlers: WebSocketHandlers) {
  const {
    updateQACheckpoint,
    handleWidgetMessage,
    handleCompleteMessage,
    setLoading,
    setWsConnection,
    handleResetQAProgress,
    setGenerationComplete,
  } = handlers;

  /**
   * Setup WebSocket message handlers
   * Routes incoming messages to appropriate handlers
   */
  const setupWebSocketHandlers = useCallback((ws: WebSocket) => {
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        switch (data.type) {
          case "qa_progress":
            updateQACheckpoint(data.data.checkpoint, data.data.status as QACheckpointStatus, data.data.details);
            break;

          case "widget":
            handleWidgetMessage(data.data);
            break;

          case "complete":
            handleCompleteMessage(data.data);
            ws.close();
            break;

          case "error":
            console.error("🔴 Error:", data.message);
            setLoading(false);
            ws.close();
            break;

          default:
            console.warn("Unknown message type:", data);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };
  }, [updateQACheckpoint, handleWidgetMessage, handleCompleteMessage, setLoading]);

  /**
   * Connect to WebSocket server
   * @returns WebSocket connection
   */
  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket(`${API_CONFIG.URL.replace("http", "ws")}/api/v1/ws/generate-widget`);

    ws.onopen = () => {
      console.log("🔌 WebSocket connected");
      setWsConnection(ws);
    };

    ws.onerror = (error) => {
      console.error("🔴 WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("🔌 WebSocket closed");
      setWsConnection(null);
    };

    return ws;
  }, [setWsConnection]);

  /**
   * Generate content using WebSocket connection
   * @param prompt - User prompt for content generation
   */
  const generateContentWithWebSocket = useCallback(async (prompt: string) => {
    if (!prompt.trim()) return;

    setLoading(true);
    handleResetQAProgress();
    setGenerationComplete(false);

    const ws = connectWebSocket();
    setupWebSocketHandlers(ws);

    // Send query once connected
    ws.onopen = () => {
      console.log("🔌 WebSocket connected, sending query");
      ws.send(JSON.stringify({
        query: prompt,
        device_context: "desktop",
      }));
    };
  }, [connectWebSocket, handleResetQAProgress, setupWebSocketHandlers, setLoading, setGenerationComplete]);

  return {
    setupWebSocketHandlers,
    connectWebSocket,
    generateContentWithWebSocket,
  };
}
