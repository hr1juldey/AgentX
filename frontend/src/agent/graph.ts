/**
 * LangGraph state definition for Real AgentX v0.1.
 *
 * Mirrors the Python AgentState from agentx/agent/state.py.
 * This file must be kept in sync with the backend state definition.
 *
 * Key patterns:
 * - messages: Accumulates with each agent step
 * - ui: Server-driven UI messages (widget components)
 * - session_id: Tracks conversation session
 * - reasoning_steps: Counter for dual-pass analyst
 * - total_tool_calls: Tool usage tracking
 * - contextualized_data: Reranked search results
 */

import { z } from 'zod';
import type { UIComponentMessage } from '@/types/websocket';

/**
 * Base message type (mirrors langchain_core.messages.BaseMessage).
 */
export const BaseMessageSchema = z.object({
  content: z.string(),
  type: z.enum(['human', 'ai', 'system', 'tool', 'function']),
  additional_kwargs: z.record(z.any()).optional(),
  response_metadata: z.record(z.any()).optional(),
  id: z.string().optional(),
});

export type BaseMessage = z.infer<typeof BaseMessageSchema>;

/**
 * UI Message type (mirrors langgraph.graph.ui.AnyUIMessage).
 *
 * These are pushed via push_ui_message() on the backend and
 * rendered via LoadExternalComponent on the frontend.
 */
export const UIMessageSchema = z.object({
  id: z.string(),
  name: z.string(), // Widget type: 'card', 'markdown', 'form', etc.
  props: z.record(z.any()), // Widget props: title, content, colors, etc.
});

export type UIMessage = z.infer<typeof UIMessageSchema>;

/**
 * AgentState - mirrors Python AgentState TypedDict.
 *
 * From agentx/agent/state.py:
 * ```python
 * class AgentState(TypedDict, total=False):
 *     messages: Annotated[Sequence[BaseMessage], add_messages]
 *     ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]
 *     session_id: str | None
 *     reasoning_steps: int
 *     total_tool_calls: int
 *     contextualized_data: dict[str, object]
 * ```
 */
export const AgentStateSchema = z.object({
  messages: z.array(BaseMessageSchema),
  ui: z.array(UIMessageSchema),
  session_id: z.string().nullable(),
  reasoning_steps: z.number().default(0),
  total_tool_calls: z.number().default(0),
  contextualized_data: z.record(z.any()).optional(),
});

export type AgentState = z.infer<typeof AgentStateSchema>;

/**
 * Empty state for initialization.
 */
export function createEmptyState(threadId?: string): AgentState {
  return {
    messages: [],
    ui: [],
    session_id: threadId ?? null,
    reasoning_steps: 0,
    total_tool_calls: 0,
    contextualized_data: undefined,
  };
}

/**
 * UI message reducer - mirrors Python's ui_message_reducer.
 *
 * Appends new UI messages to the state without duplicates.
 * Each widget has a unique id from push_ui_message().
 */
export function uiMessageReducer(
  existing: UIMessage[],
  incoming: UIMessage | UIMessage[]
): UIMessage[] {
  const incomingArray = Array.isArray(incoming) ? incoming : [incoming];
  const existingIds = new Set(existing.map((m) => m.id));
  const newMessages = incomingArray.filter((m) => !existingIds.has(m.id));
  return [...existing, ...newMessages];
}

/**
 * Message reducer - mirrors Python's add_messages annotation.
 *
 * Appends new messages to the state.
 */
export function addMessages(existing: BaseMessage[], incoming: BaseMessage[]): BaseMessage[] {
  return [...existing, ...incoming];
}
