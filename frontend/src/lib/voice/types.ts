/**
 * Voice client types for WebSocket communication with AgentX.
 */

/**
 * Voice message types matching kyutai protocol.
 */
export enum VoiceMessageType {
  CONFIG = 'Config',
  AUDIO = 'Audio',
  TEXT = 'Text',
  ERROR = 'Error',
  EOS = 'Eos',
  HEARTBEAT = 'Heartbeat',
  INTERRUPT = 'Interrupt',
}

/**
 * Voice message structure.
 */
export interface VoiceMessage {
  type: VoiceMessageType;
  data: string | Record<string, unknown>;
  sessionId: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

/**
 * Voice client configuration.
 */
export interface VoiceClientConfig {
  url: string; // ws://localhost:8019/ws/voice
  sessionId?: string;
  reconnectInterval?: number; // Default: 1000ms
  maxReconnectAttempts?: number; // Default: 10
}

/**
 * Voice client connection state.
 */
export interface VoiceClientState {
  connected: boolean;
  reconnecting: boolean;
  reconnectAttempts: number;
  lastError: string | null;
}

/**
 * Voice client event handlers.
 */
export type VoiceMessageHandler = (message: VoiceMessage) => void;
export type VoiceErrorHandler = (error: Error) => void;
export type VoiceStateChangeHandler = (state: VoiceClientState) => void;

/**
 * Voice client events.
 */
export interface VoiceClientEvents {
  onConnected?: () => void;
  onDisconnected?: () => void;
  onMessage?: VoiceMessageHandler;
  onError?: VoiceErrorHandler;
  onStateChange?: VoiceStateChangeHandler;
}
