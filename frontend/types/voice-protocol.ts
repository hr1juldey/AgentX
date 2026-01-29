import { z } from 'zod';

/**
 * Kyutai WebSocket message types.
 */
export const KyutaiMessageType = z.enum([
  'Config',
  'Audio',
  'Text',
  'Error',
  'Eos',
  'Heartbeat',
]);

export type KyutaiMessageType = z.infer<typeof KyutaiMessageType>;

/**
 * Kyutai WebSocket message schema.
 */
export const KyutaiMessageSchema = z.object({
  type: KyutaiMessageType,
  data: z.unknown(),
  sessionId: z.string(),
  timestamp: z.number(),
  metadata: z.record(z.unknown()).optional(),
});

export type KyutaiMessage = z.infer<typeof KyutaiMessageSchema>;

/**
 * Message role in conversation.
 */
export const MessageRole = z.enum([
  'user',
  'assistant',
  'system',
]);

export type MessageRole = z.infer<typeof MessageRole>;

/**
 * Conversation message schema.
 */
export const ConversationMessageSchema = z.object({
  messageId: z.string(),
  role: MessageRole,
  content: z.string(),
  timestamp: z.string().datetime(),
  metadata: z.record(z.unknown()).optional(),
});

export type ConversationMessage = z.infer<typeof ConversationMessageSchema>;

/**
 * Conversation context schema.
 */
export const ConversationContextSchema = z.object({
  currentTopic: z.string().optional(),
  entities: z.record(z.unknown()).optional(),
  sentiment: z.string().optional(),
  language: z.string().default('en'),
  timezone: z.string().default('UTC'),
});

export type ConversationContext = z.infer<typeof ConversationContextSchema>;

/**
 * Conversation session schema.
 */
export const ConversationSessionSchema = z.object({
  sessionId: z.string(),
  messages: z.array(ConversationMessageSchema).default([]),
  context: ConversationContextSchema.default({
    language: 'en',
    timezone: 'UTC',
  }),
  createdAt: z.string().datetime(),
  lastActivityAt: z.string().datetime(),
});

export type ConversationSession = z.infer<typeof ConversationSessionSchema>;
