/** Zod schemas for API requests.
 *
 * Matches backend Pydantic models in agentx/application/dtos/
 */

import { z } from 'zod';

// ExecuteAgentQueryRequest
export const ExecuteAgentQueryRequestSchema = z.object({
  query: z.string(),
  user_id: z.string().optional(),
  session_id: z.string().uuid().optional(),
});

export type ExecuteAgentQueryRequest = z.infer<typeof ExecuteAgentQueryRequestSchema>;

// GenerateWidgetRequest
export const GenerateWidgetRequestSchema = z.object({
  query: z.string(),
  widget_type: z.string().optional(),
  context: z.record(z.unknown()).optional(),
});

export type GenerateWidgetRequest = z.infer<typeof GenerateWidgetRequestSchema>;

// SearchRequest
export const SearchRequestSchema = z.object({
  query: z.string(),
  max_hops: z.number().int().default(3).optional(),
  device_context: z.string().default('desktop').optional(),
});

export type SearchRequest = z.infer<typeof SearchRequestSchema>;
