/**
 * Voice client for WebSocket communication with AgentX.
 */

import { v4 as uuidv4 } from 'uuid';
import {
  VoiceMessage,
  VoiceMessageType,
  VoiceClientConfig,
  VoiceClientState,
} from './types';

export class VoiceClient {
  private ws: WebSocket | null = null;
  private config: Required<VoiceClientConfig>;
  private state: VoiceClientState;
  private messageHandlers: Map<VoiceMessageType, (msg: VoiceMessage) => void>;

  constructor(config: VoiceClientConfig) {
    this.config = {
      ...config,
      sessionId: config.sessionId || uuidv4(),
      reconnectInterval: config.reconnectInterval ?? 1000,
      maxReconnectAttempts: config.maxReconnectAttempts ?? 10,
    };
    this.state = {
      connected: false,
      reconnecting: false,
      reconnectAttempts: 0,
      lastError: null,
    };
    this.messageHandlers = new Map();
  }

  connect(): void {
    const url = `${this.config.url}?sessionId=${this.config.sessionId}`;
    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      this.state.connected = true;
      this.state.reconnecting = false;
      this.state.reconnectAttempts = 0;
      this.state.lastError = null;
      console.log('[VoiceClient] Connected');
    };

    this.ws.onmessage = (event) => {
      const message: VoiceMessage = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.ws.onclose = () => {
      this.state.connected = false;
      if (
        !this.state.reconnecting &&
        this.state.reconnectAttempts < this.config.maxReconnectAttempts
      ) {
        this.reconnect();
      }
    };

    this.ws.onerror = () => {
      this.state.lastError = 'WebSocket error';
      console.error('[VoiceClient] WebSocket error');
    };
  }

  private reconnect(): void {
    this.state.reconnecting = true;
    this.state.reconnectAttempts++;
    const delay =
      this.config.reconnectInterval * Math.pow(2, this.state.reconnectAttempts - 1);
    console.log(
      `[VoiceClient] Reconnecting in ${delay}ms (attempt ${this.state.reconnectAttempts})`
    );
    setTimeout(() => this.connect(), delay);
  }

  private handleMessage(message: VoiceMessage): void {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message);
    }
  }

  sendAudio(audioBase64: string): void {
    const message: VoiceMessage = {
      type: VoiceMessageType.AUDIO,
      data: audioBase64,
      sessionId: this.config.sessionId,
      timestamp: Date.now() / 1000,
    };
    this.send(message);
  }

  sendInterrupt(): void {
    const message: VoiceMessage = {
      type: VoiceMessageType.INTERRUPT,
      data: 'interrupt',
      sessionId: this.config.sessionId,
      timestamp: Date.now() / 1000,
    };
    this.send(message);
  }

  on(messageType: VoiceMessageType, handler: (msg: VoiceMessage) => void): void {
    this.messageHandlers.set(messageType, handler);
  }

  private send(message: VoiceMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.state.connected = false;
    this.state.reconnecting = false;
  }

  getState(): VoiceClientState {
    return { ...this.state };
  }
}
