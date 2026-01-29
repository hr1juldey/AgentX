/** Zod schemas for WebSocket messages.
 *
 * Matches backend Pydantic models in agentx/ui/protocols/websocket_messages.py
 */

import { z } from 'zod';

// WebSocketMessageType enum
export const WebSocketMessageTypeSchema = z.enum([
  'QUERY',
  'RESPONSE',
  'TOKEN',
  'REASONING_STEP',
  'TOOL_CALL',
  'TOOL_RESULT',
  'ERROR',
  'PING',
  'PONG',
  'DESCRIPTOR_CREATE',
  'DESCRIPTOR_UPDATE',
  'DESCRIPTOR_REMOVE',
  'FORM_SHOW',
  'FORM_SUBMIT',
  'PROGRESS_UPDATE',
]);

export type WebSocketMessageType = z.infer<typeof WebSocketMessageTypeSchema>;

// Base WebSocketMessage
export const WebSocketMessageSchema = z.object({
  message_id: z.string(),
  message_type: WebSocketMessageTypeSchema,
  session_id: z.string().nullable(),
  timestamp: z.number(),
  data: z.record(z.unknown()),
});

export type WebSocketMessage = z.infer<typeof WebSocketMessageSchema>;

// Query message
export const QueryMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    query: z.string(),
  }),
});

// Response message
export const ResponseMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    response: z.string(),
    reasoning: z.string().optional(),
    ui_components: z.array(z.any()).optional(),
    tool_calls: z.array(z.any()).optional(),
  }),
});

// Token message (for streaming)
export const TokenMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    token: z.string(),
    is_final: z.boolean().default(false),
  }),
});

// ReasoningStep message
export const ReasoningStepMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    step: z.number(),
    reasoning: z.string(),
  }),
});

// ToolCall message
export const ToolCallMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    tool_name: z.string(),
    parameters: z.record(z.unknown()),
    tool_call_id: z.string(),
  }),
});

// ToolResult message
export const ToolResultMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    tool_call_id: z.string(),
    result: z.unknown(),
    error: z.string().optional(),
  }),
});

// Error message
export const ErrorMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    error: z.string(),
    code: z.string().optional(),
  }),
});

// PING/PONG messages
export const PingMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({}).optional(),
});

export const PongMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({}).optional(),
});

// DescriptorCreate message
export const DescriptorCreateMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    descriptor: z.any(), // UIDescriptor
  }),
});

// FormShow message
export const FormShowMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    form_id: z.string(),
    fields: z.array(z.any()),
  }),
});

// FormSubmit message
export const FormSubmitMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    form_id: z.string(),
    values: z.record(z.unknown()),
  }),
});

// ProgressUpdate message
export const ProgressUpdateMessageSchema = WebSocketMessageSchema.extend({
  data: z.object({
    progress: z.number().int().min(0).max(100),
    status: z.string(),
    indeterminate: z.boolean().default(false),
  }),
});
