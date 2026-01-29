/**
 * Conversation state helpers for voice interactions.
 */

import { ConversationMessage, ConversationSession } from '../../types/voice-protocol';

/**
 * Create a new conversation session.
 */
export function createConversationSession(
  sessionId: string
): ConversationSession {
  return {
    sessionId,
    messages: [],
    context: {
      language: 'en',
      timezone: 'UTC',
    },
    createdAt: new Date().toISOString(),
    lastActivityAt: new Date().toISOString(),
  };
}

/**
 * Add a message to the conversation session.
 */
export function addMessageToSession(
  session: ConversationSession,
  role: 'user' | 'assistant' | 'system',
  content: string
): ConversationSession {
  const message: ConversationMessage = {
    messageId: crypto.randomUUID(),
    role,
    content,
    timestamp: new Date().toISOString(),
  };

  return {
    ...session,
    messages: [...session.messages, message],
    lastActivityAt: new Date().toISOString(),
  };
}

/**
 * Get conversation history with limit.
 */
export function getConversationHistory(
  session: ConversationSession,
  limit: number = 20
): ConversationMessage[] {
  return session.messages.slice(-limit);
}

/**
 * Check if session is expired (5 minutes timeout).
 */
export function isSessionExpired(session: ConversationSession, timeoutMs: number = 300000): boolean {
  const lastActivity = new Date(session.lastActivityAt).getTime();
  const now = Date.now();
  return now - lastActivity > timeoutMs;
}
