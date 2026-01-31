/**
 * Memory API schemas with Zod validation.
 *
 * Matches backend Pydantic DTOs from C005 memory-rag.
 */

import { z } from 'zod';

// Temporal types enum
export const TemporalTypeSchema = z.enum([
  'preference',
  'state',
  'event',
  'plan',
  'fact',
] as const);

export type TemporalType = z.infer<typeof TemporalTypeSchema>;

// Request DTOs

export const StoreMemoryRequestSchema = z.object({
  content: z.string().min(1, 'Memory content is required'),
  user_id: z.string().min(1, 'User ID is required'),
  temporal_type: TemporalTypeSchema.default('fact'),
  tier: z.number().int().min(2).max(3).default(3),
  session_id: z.string().uuid().optional(),
  metadata: z.record(z.any()).optional(),
});

export type StoreMemoryRequest = z.infer<typeof StoreMemoryRequestSchema>;

export const SearchMemoryRequestSchema = z.object({
  query: z.string().min(1, 'Search query is required'),
  user_id: z.string().min(1, 'User ID is required'),
  time_filter: z.enum(['recent', 'historical', 'all']).default('all'),
  tier: z.number().int().min(2).max(3).default(3),
  session_id: z.string().uuid().optional(),
  max_results: z.number().int().min(1).max(100).default(10),
  temporal_types: z.array(TemporalTypeSchema).optional(),
});

export type SearchMemoryRequest = z.infer<typeof SearchMemoryRequestSchema>;

export const ConsolidateMemoryRequestSchema = z.object({
  user_id: z.string().min(1, 'User ID is required'),
  session_id: z.string().min(1, 'Session ID is required'),
  min_memories: z.number().int().min(1).default(5),
});

export type ConsolidateMemoryRequest = z.infer<typeof ConsolidateMemoryRequestSchema>;

// Response DTOs

export const SearchResultSchema = z.object({
  memory_id: z.string().uuid(),
  content: z.string(),
  temporal_type: z.string(),
  created_at: z.string().datetime(),
  valid_until: z.string().datetime().nullable(),
  score: z.number().min(0).max(1),
  superseded: z.boolean().default(false),
});

export type SearchResult = z.infer<typeof SearchResultSchema>;

export const SearchMemoryResponseSchema = z.object({
  results: z.array(SearchResultSchema),
  total_found: z.number().int(),
  query_time_ms: z.number().int(),
});

export type SearchMemoryResponse = z.infer<typeof SearchMemoryResponseSchema>;

export const StoreMemoryResponseSchema = z.object({
  memory_id: z.string().uuid(),
  content: z.string(),
  user_id: z.string(),
  temporal_type: z.string(),
  created_at: z.string().datetime(),
  valid_from: z.string().datetime(),
  valid_until: z.string().datetime().nullable(),
  tier: z.number(),
  message: z.string(),
});

export type StoreMemoryResponse = z.infer<typeof StoreMemoryResponseSchema>;

export const ConsolidateMemoryResponseSchema = z.object({
  session_id: z.string(),
  user_id: z.string(),
  consolidated_at: z.string().datetime().nullable(),
  memories_consolidated: z.number().int(),
  memories_discarded: z.number().int(),
  consolidation_summary: z.string(),
});

export type ConsolidateMemoryResponse = z.infer<typeof ConsolidateMemoryResponseSchema>;

export const HealthResponseSchema = z.object({
  status: z.string(),
  qdrant_connected: z.boolean(),
  timestamp: z.string().datetime(),
});

export type HealthResponse = z.infer<typeof HealthResponseSchema>;
