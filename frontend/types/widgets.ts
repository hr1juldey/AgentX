/** Widget types matching backend agentx.domain.models.widget_selection.
 *
 * Zod schemas for widget specifications and progressive disclosure.
 */

import { z } from 'zod';

// WidgetType enum matching backend WidgetType
export const WidgetTypeSchema = z.enum([
  'data_table',
  'chart',
  'timeline',
  'map',
  'text_card',
]);

export type WidgetType = z.infer<typeof WidgetTypeSchema>;

// ContentPattern enum matching backend ContentPattern
export const ContentPatternSchema = z.enum([
  'comparison',
  'temporal',
  'geographic',
  'ranking',
  'numerical',
  'textual',
]);

export type ContentPattern = z.infer<typeof ContentPatternSchema>;

// WidgetSpecification matching backend
export const WidgetSpecificationSchema = z.object({
  widget_type: WidgetTypeSchema,
  title: z.string(),
  content: z.record(z.unknown()).default({}),
  priority: z.number().int().min(1).max(10).default(5),
  sources: z.array(z.string()).default([]),
});

export type WidgetSpecification = z.infer<typeof WidgetSpecificationSchema>;

// WidgetRevealEvent for streaming
export const WidgetRevealEventSchema = z.object({
  event_type: z.literal('widget_reveal'),
  widget: WidgetSpecificationSchema,
  index: z.number().int().min(0),
  total: z.number().int().min(0),
});

export type WidgetRevealEvent = z.infer<typeof WidgetRevealEventSchema>;
