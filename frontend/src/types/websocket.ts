/**
 * WebSocket message types for Real AgentX v0.1.
 *
 * Defines bidirectional communication schemas for real-time agent interaction.
 */

import { z } from 'zod';

/**
 * Message types for WebSocket communication.
 */
export const MessageType = z.enum([
  // Client -> Server
  'query',
  'voice_data',
  'interrupt',
  'ping',
  // Server -> Client
  'response',
  'reasoning',
  'ui_component',
  'tool_call',
  'tool_result',
  'error',
  'pong',
  'status',
]);

export type MessageType = z.infer<typeof MessageType>;

/**
 * Base WebSocket message schema.
 */
export const WebSocketMessageSchema = z.object({
  message_id: z.string().uuid(),
  message_type: MessageType,
  session_id: z.string().uuid().nullable(),
  timestamp: z.number(),
  data: z.record(z.any()),
});

export type WebSocketMessage = z.infer<typeof WebSocketMessageSchema>;

/**
 * Query message (client -> server).
 */
export const QueryMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('query'),
  data: z.object({
    query: z.string().min(1),
  }),
});

export type QueryMessage = z.infer<typeof QueryMessageSchema>;

/**
 * Response message (server -> client).
 */
export const ResponseMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('response'),
  data: z.object({
    content: z.string(),
    is_complete: z.boolean(),
    is_delta: z.boolean().default(false),
  }),
});

export type ResponseMessage = z.infer<typeof ResponseMessageSchema>;

/**
 * UI component message (server -> client).
 * Server-driven UI pattern from C007.
 */
export const UIComponentMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('ui_component'),
  data: z.object({
    component_type: z.string(),
    props: z.record(z.any()),
    merge: z.boolean().default(false),
    component_id: z.string().uuid(),
  }),
});

export type UIComponentMessage = z.infer<typeof UIComponentMessageSchema>;

/**
 * Tool call message (server -> client).
 */
export const ToolCallMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('tool_call'),
  data: z.object({
    tool_name: z.string(),
    parameters: z.record(z.any()),
    call_id: z.string().uuid(),
  }),
});

export type ToolCallMessage = z.infer<typeof ToolCallMessageSchema>;

/**
 * Error message (server -> client).
 */
export const ErrorMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('error'),
  data: z.object({
    error_message: z.string(),
    error_code: z.string().optional(),
  }),
});

export type ErrorMessage = z.infer<typeof ErrorMessageSchema>;

/**
 * Status message (server -> client).
 */
export const StatusMessageSchema = WebSocketMessageSchema.extend({
  message_type: z.literal('status'),
  data: z.object({
    status: z.string(),
    details: z.string().optional(),
  }),
});

export type StatusMessage = z.infer<typeof StatusMessageSchema>;

/**
 * Union of all client-to-server messages.
 */
export const ClientMessageSchema = z.discriminatedUnion('message_type', [
  QueryMessageSchema,
]);

export type ClientMessage = z.infer<typeof ClientMessageSchema>;

/**
 * Union of all server-to-client messages.
 */
export const ServerMessageSchema = z.discriminatedUnion('message_type', [
  ResponseMessageSchema,
  UIComponentMessageSchema,
  ToolCallMessageSchema,
  ErrorMessageSchema,
  StatusMessageSchema,
]);

export type ServerMessage = z.infer<typeof ServerMessageSchema>;
