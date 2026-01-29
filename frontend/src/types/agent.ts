/**
 * Agent types for Real AgentX v0.1.
 *
 * Zod schemas matching backend Pydantic DTOs (C002 data contracts alignment).
 * Frontend TypeScript types mirror backend Python types.
 */

import { z } from 'zod';

/**
 * Session states matching backend SessionState enum.
 */
export const SessionState = z.enum([
  'initializing',
  'active',
  'paused',
  'closed',
  'error',
]);

export type SessionState = z.infer<typeof SessionState>;

/**
 * Tool execution status matching backend ToolStatus enum.
 */
export const ToolStatus = z.enum([
  'pending',
  'running',
  'success',
  'error',
]);

export type ToolStatus = z.infer<typeof ToolStatus>;

/**
 * Execute agent query request (matches ExecuteAgentQueryRequest).
 */
export const ExecuteAgentQueryRequestSchema = z.object({
  query: z.string().min(1),
  session_id: z.string().uuid().nullable(),
  user_id: z.string().nullable(),
  context: z.string().nullable(),
});

export type ExecuteAgentQueryRequest = z.infer<typeof ExecuteAgentQueryRequestSchema>;

/**
 * Tool call DTO (matches ToolCallDTO).
 */
export const ToolCallDTOSchema = z.object({
  tool_name: z.string(),
  parameters: z.record(z.any()).default({}),
  result: z.any().nullable(),
  status: ToolStatus.default('pending'),
  timestamp: z.number(), // Unix timestamp
});

export type ToolCallDTO = z.infer<typeof ToolCallDTOSchema>;

/**
 * UI component DTO (matches UIComponentDTO).
 */
export const UIComponentDTOSchema = z.object({
  component_id: z.string(),
  component_type: z.string(),
  props: z.record(z.any()).default({}),
  merge: z.boolean().default(false),
});

export type UIComponentDTO = z.infer<typeof UIComponentDTOSchema>;

/**
 * Execute agent query response (matches ExecuteAgentQueryResponse).
 */
export const ExecuteAgentQueryResponseSchema = z.object({
  session_id: z.string(),
  response: z.string(),
  reasoning: z.string(),
  ui_components: z.array(UIComponentDTOSchema).default([]),
  tool_calls: z.array(ToolCallDTOSchema).default([]),
  sources: z.array(z.string()).default([]),
  timestamp: z.number(), // Unix timestamp
});

export type ExecuteAgentQueryResponse = z.infer<typeof ExecuteAgentQueryResponseSchema>;

/**
 * Session status DTO (matches SessionStatusDTO).
 */
export const SessionStatusDTOSchema = z.object({
  session_id: z.string(),
  state: SessionState,
  created_at: z.number(), // Unix timestamp
  last_activity_at: z.number(), // Unix timestamp
  current_reasoning_step: z.number().default(0),
  total_tool_calls: z.number().default(0),
});

export type SessionStatusDTO = z.infer<typeof SessionStatusDTOSchema>;

/**
 * Create session command (matches CreateSessionCommand).
 */
export const CreateSessionCommandSchema = z.object({
  user_id: z.string().min(64).max(64), // SHA-256 hash
  initial_context: z.array(z.string()).default([]),
});

export type CreateSessionCommand = z.infer<typeof CreateSessionCommandSchema>;

/**
 * Pause session command (matches PauseSessionCommand).
 */
export const PauseSessionCommandSchema = z.object({
  session_id: z.string().uuid(),
  reason: z.string().nullable(),
});

export type PauseSessionCommand = z.infer<typeof PauseSessionCommandSchema>;

/**
 * Resume session command (matches ResumeSessionCommand).
 */
export const ResumeSessionCommandSchema = z.object({
  session_id: z.string().uuid(),
  context: z.array(z.string()).default([]),
});

export type ResumeSessionCommand = z.infer<typeof ResumeSessionCommandSchema>;

/**
 * Close session command (matches CloseSessionCommand).
 */
export const CloseSessionCommandSchema = z.object({
  session_id: z.string().uuid(),
  reason: z.string().nullable(),
});

export type CloseSessionCommand = z.infer<typeof CloseSessionCommandSchema>;

/**
 * Streaming chunk types (matches StreamChunk, ReasoningStep).
 */
export const StreamChunkType = z.enum([
  'text',
  'reasoning',
  'tool_call',
  'ui_component',
  'error',
]);

export type StreamChunkType = z.infer<typeof StreamChunkType>;

export const StreamChunkSchema = z.object({
  chunk_type: StreamChunkType,
  content: z.record(z.any()),
  sequence_id: z.number().min(0),
  timestamp: z.number(), // Unix timestamp
});

export type StreamChunk = z.infer<typeof StreamChunkSchema>;

export const ReasoningStepSchema = z.object({
  step_number: z.number().min(1),
  thought: z.string(),
  action: z.string(),
  observation: z.string().default(''),
  confidence: z.number().min(0).max(1).default(0.5),
});

export type ReasoningStep = z.infer<typeof ReasoningStepSchema>;
