/**
 * UI descriptor types for Real AgentX server-driven UI (C007).
 *
 * These types map to Python descriptor classes in backend.
 * Zod schemas for runtime validation.
 */

import { z } from 'zod';

/**
 * UI component types (12 frozen widget types from C007).
 */
export const WidgetType = z.enum([
  'markdown',
  'card',
  'form',
  'progress',
  'action',
  'confirmation',
  'voice',
  'image',
  'gallery',
  'chart',
  'searchResult',
  'hopProgress',
  'citationCard',
]);

export type WidgetType = z.infer<typeof WidgetType>;

/**
 * Base UI descriptor schema.
 */
export const BaseUIDescriptorSchema = z.object({
  descriptor_id: z.string().uuid(),
  component_type: WidgetType,
  props: z.record(z.any()),
});

export type BaseUIDescriptor = z.infer<typeof BaseUIDescriptorSchema>;

/**
 * Markdown component descriptor.
 */
export const MarkdownDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('markdown'),
  props: z.object({
    content: z.string(),
    format: z.enum(['markdown', 'plain']).default('markdown'),
  }),
});

export type MarkdownDescriptor = z.infer<typeof MarkdownDescriptorSchema>;

/**
 * Card component descriptor.
 */
export const CardDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('card'),
  props: z.object({
    title: z.string(),
    content: z.string(),
    actions: z.array(z.object({
      label: z.string(),
      action: z.string(),
      primary: z.boolean().default(false),
    })).default([]),
  }),
});

export type CardDescriptor = z.infer<typeof CardDescriptorSchema>;

/**
 * Form component descriptor.
 */
export const FormDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('form'),
  props: z.object({
    fields: z.array(z.object({
      name: z.string(),
      label: z.string(),
      type: z.enum(['text', 'textarea', 'select', 'checkbox', 'radio']),
      required: z.boolean().default(false),
      options: z.array(z.string()).optional(),
      placeholder: z.string().optional(),
    })),
    submit_url: z.string().url(),
    method: z.enum(['GET', 'POST']).default('POST'),
  }),
});

export type FormDescriptor = z.infer<typeof FormDescriptorSchema>;

/**
 * Progress component descriptor.
 */
export const ProgressDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('progress'),
  props: z.object({
    progress: z.number().min(0).max(100),
    status: z.string(),
    indeterminate: z.boolean().default(false),
  }),
});

export type ProgressDescriptor = z.infer<typeof ProgressDescriptorSchema>;

/**
 * Action component descriptor.
 */
export const ActionDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('action'),
  props: z.object({
    label: z.string(),
    action: z.string(),
    primary: z.boolean().default(true),
  }),
});

export type ActionDescriptor = z.infer<typeof ActionDescriptorSchema>;

/**
 * Confirmation component descriptor.
 */
export const ConfirmationDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('confirmation'),
  props: z.object({
    title: z.string(),
    message: z.string(),
    confirm_label: z.string().default('Confirm'),
    cancel_label: z.string().default('Cancel'),
    on_confirm: z.string(),
  }),
});

export type ConfirmationDescriptor = z.infer<typeof ConfirmationDescriptorSchema>;

/**
 * Voice component descriptor.
 */
export const VoiceDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('voice'),
  props: z.object({
    state: z.enum(['idle', 'listening', 'processing', 'speaking']),
    transcript: z.string().default(''),
  }),
});

export type VoiceDescriptor = z.infer<typeof VoiceDescriptorSchema>;

/**
 * Image component descriptor.
 */
export const ImageDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('image'),
  props: z.object({
    url: z.string().url(),
    alt: z.string().default(''),
    caption: z.string().default(''),
  }),
});

export type ImageDescriptor = z.infer<typeof ImageDescriptorSchema>;

/**
 * Gallery component descriptor.
 */
export const GalleryDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('gallery'),
  props: z.object({
    images: z.array(z.object({
      url: z.string().url(),
      alt: z.string().default(''),
      caption: z.string().default(''),
    })),
    columns: z.number().min(1).max(6).default(3),
  }),
});

export type GalleryDescriptor = z.infer<typeof GalleryDescriptorSchema>;

/**
 * Chart component descriptor.
 */
export const ChartDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('chart'),
  props: z.object({
    chart_type: z.enum(['line', 'bar', 'pie']),
    data: z.record(z.any()),
    options: z.record(z.any()).default({}),
  }),
});

export type ChartDescriptor = z.infer<typeof ChartDescriptorSchema>;

/**
 * Search result component descriptor.
 */
export const SearchResultDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('searchResult'),
  props: z.object({
    query: z.string(),
    results: z.array(z.object({
      title: z.string(),
      url: z.string().url(),
      snippet: z.string(),
    })),
  }),
});

export type SearchResultDescriptor = z.infer<typeof SearchResultDescriptorSchema>;

/**
 * Hop progress component descriptor (multi-hop RAG).
 */
export const HopProgressDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('hopProgress'),
  props: z.object({
    current_hop: z.number().min(1),
    total_hops: z.number().min(1),
    hop_status: z.array(z.object({
      hop_number: z.number(),
      status: z.enum(['pending', 'running', 'complete', 'error']),
      result_count: z.number().default(0),
    })),
  }),
});

export type HopProgressDescriptor = z.infer<typeof HopProgressDescriptorSchema>;

/**
 * Citation card component descriptor.
 */
export const CitationCardDescriptorSchema = BaseUIDescriptorSchema.extend({
  component_type: z.literal('citationCard'),
  props: z.object({
    source: z.string(),
    content: z.string(),
    url: z.string().url().default(''),
    relevance: z.number().min(0).max(1),
  }),
});

export type CitationCardDescriptor = z.infer<typeof CitationCardDescriptorSchema>;

/**
 * Union of all descriptor types (12 frozen widget types from C007).
 */
export const AnyUIDescriptorSchema = z.discriminatedUnion('component_type', [
  MarkdownDescriptorSchema,
  CardDescriptorSchema,
  FormDescriptorSchema,
  ProgressDescriptorSchema,
  ActionDescriptorSchema,
  ConfirmationDescriptorSchema,
  VoiceDescriptorSchema,
  ImageDescriptorSchema,
  GalleryDescriptorSchema,
  ChartDescriptorSchema,
  SearchResultDescriptorSchema,
  HopProgressDescriptorSchema,
  CitationCardDescriptorSchema,
]);

export type AnyUIDescriptor = z.infer<typeof AnyUIDescriptorSchema>;
