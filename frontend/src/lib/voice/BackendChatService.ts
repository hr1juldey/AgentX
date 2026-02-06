/**
 * Backend Chat Service - LangGraph API communication.
 *
 * Single Responsibility: Communicate with backend /ws/chat endpoint.
 * Following CLAUDE_POLICY.md: Absolute imports, file size < 100 lines.
 */

'use client';

// ===== CONFIGURATION =====
const BACKEND_CHAT_WS_URL = 'ws://localhost:8015/api/v1/ws/chat';
const CHAT_TIMEOUT_MS = 30000; // 30 seconds

// ===== TYPES =====
export interface ChatMessage {
  message_type: 'query' | 'response' | 'error';
  data: { query?: string; response?: string; error?: string };
  session_id: string;
}

export interface ChatResponse {
  success: boolean;
  response: string | null;
  error?: string;
}

// ===== SERVICE CLASS =====
class BackendChatService {
  private ws: WebSocket | null = null;

  /**
   * Send query to backend and get response.
   *
   * @param query - User query text
   * @param sessionId - Session identifier for conversation continuity
   * @returns Promise with chat response
   */
  async sendQuery(query: string, sessionId: string): Promise<ChatResponse> {
    const url = `${BACKEND_CHAT_WS_URL}?session_id=${sessionId}`;

    return new Promise<ChatResponse>((resolve, reject) => {
      // Timeout guard
      const timeout = setTimeout(() => {
        this.ws?.close();
        reject(new Error('Backend chat timeout'));
      }, CHAT_TIMEOUT_MS);

      // Create WebSocket connection
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        console.log('[BackendChat] Connected, sending query:', query);
        const message: ChatMessage = {
          message_type: 'query',
          data: { query },
          session_id: sessionId,
        };
        this.ws?.send(JSON.stringify(message));
      };

      this.ws.onmessage = (event) => {
        try {
          const msg: ChatMessage = JSON.parse(event.data);
          console.log('[BackendChat] Received:', msg.message_type);

          if (msg.message_type === 'response') {
            clearTimeout(timeout);
            const response = msg.data?.response || null;
            this.close();
            resolve({ success: true, response });
          } else if (msg.message_type === 'error') {
            clearTimeout(timeout);
            const error = msg.data?.error || 'Unknown backend error';
            this.close();
            resolve({ success: false, response: null, error });
          }
        } catch (error) {
          clearTimeout(timeout);
          this.close();
          reject(error);
        }
      };

      this.ws.onerror = () => {
        clearTimeout(timeout);
        this.close();
        reject(new Error('WebSocket connection failed'));
      };

      this.ws.onclose = () => {
        clearTimeout(timeout);
      };
    });
  }

  /** Close WebSocket connection. */
  close(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// ===== SINGLETON EXPORT =====
const instance = new BackendChatService();
export default instance;
