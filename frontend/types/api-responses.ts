/** Zod schemas for API responses.
 *
 * Matches backend Pydantic models in agentx/application/dtos/
 */

import { z } from 'zod';
import { WebSocketMessageSchema } from './websocket';

// UIComponentDTO
export const UIComponentDTOSchema = z.object({
  component_id: z.string(),
  component_type: z.string(),
  props: z.record(z.unknown()),
  merge: z.boolean().default(false),
});

export type UIComponentDTO = z.infer<typeof UIComponentDTOSchema>;

// ExecuteAgentQueryResponse
export const ExecuteAgentQueryResponseSchema = z.object({
  session_id: z.string(),
  response: z.string(),
  reasoning: z.string(),
  ui_components: z.array(UIComponentDTOSchema),
  tool_calls: z.array(z.any()),
});

export type ExecuteAgentQueryResponse = z.infer<typeof ExecuteAgentQueryResponseSchema>;

// SearchResultResponseDTO
export const SearchResultResponseDTOSchema = z.object({
  query: z.string(),
  results: z.array(z.object({
    title: z.string(),
    body: z.string(),
    link: z.string(),
    source: z.string(),
  })),
});

export type SearchResultResponseDTO = z.infer<typeof SearchResultResponseDTOSchema>;

// ErrorResponse
export const ErrorResponseSchema = z.object({
  error: z.string(),
  code: z.string().optional(),
  details: z.record(z.unknown()).optional(),
});

export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
