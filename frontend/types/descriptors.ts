/** Zod schemas for UI descriptors.
 *
 * Matches backend Pydantic models in agentx/ui/descriptors/
 */

import { z } from 'zod';

// Enum types
export const UIDescriptorTypeSchema = z.enum([
  'MARKDOWN_BLOCK',
  'CARD',
  'FORM',
  'PROGRESS',
  'ACTION',
  'CONFIRMATION',
  'VOICE',
]);

export type UIDescriptorType = z.infer<typeof UIDescriptorTypeSchema>;

// FormFieldType enum
export const FormFieldTypeSchema = z.enum([
  'text',
  'email',
  'password',
  'number',
  'textarea',
  'select',
  'checkbox',
  'radio',
]);

export type FormFieldType = z.infer<typeof FormFieldTypeSchema>;

// VoiceState enum
export const VoiceStateSchema = z.enum(['idle', 'listening', 'processing', 'speaking']);

export type VoiceState = z.infer<typeof VoiceStateSchema>;

// CardAction
export const CardActionSchema = z.object({
  label: z.string(),
  action: z.string(),
  variant: z.string().default('outline'),
});

// CardDescriptor
export const CardDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  title: z.string(),
  content: z.string(),
  actions: z.array(CardActionSchema).default([]),
  metadata: z.record(z.unknown()).default({}),
});

// FormField
export const FormFieldSchema = z.object({
  name: z.string(),
  label: z.string(),
  field_type: FormFieldTypeSchema,
  placeholder: z.string().default(''),
  required: z.boolean().default(false),
  options: z.array(z.string()).default([]),
  default_value: z.unknown().optional(),
});

// FormDescriptor
export const FormDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  title: z.string(),
  fields: z.array(FormFieldSchema),
  submit_url: z.string(),
  method: z.string().default('POST'),
  metadata: z.record(z.unknown()).default({}),
});

// ProgressDescriptor
export const ProgressDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  progress: z.number().int().min(0).max(100).default(0),
  status: z.string(),
  indeterminate: z.boolean().default(false),
  metadata: z.record(z.unknown()).default({}),
});

// ActionDescriptor
export const ActionDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  label: z.string(),
  action: z.string(),
  primary: z.boolean().default(true),
  metadata: z.record(z.unknown()).default({}),
});

// ConfirmationDescriptor
export const ConfirmationDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  title: z.string(),
  message: z.string(),
  confirm_label: z.string().default('Confirm'),
  cancel_label: z.string().default('Cancel'),
  on_confirm: z.string(),
  metadata: z.record(z.unknown()).default({}),
});

// VoiceDescriptor
export const VoiceDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  state: VoiceStateSchema.default('idle'),
  transcript: z.string().default(''),
  metadata: z.record(z.unknown()).default({}),
});

// MarkdownBlockDescriptor
export const MarkdownBlockDescriptorSchema = z.object({
  id: z.string(),
  type: UIDescriptorTypeSchema,
  content: z.string(),
  format: z.string().default('markdown'),
  metadata: z.record(z.unknown()).default({}),
});

// Union discriminator for all descriptors
export const UIDescriptorSchema = z.discriminatedUnion('type', [
  MarkdownBlockDescriptorSchema,
  CardDescriptorSchema,
  FormDescriptorSchema,
  ProgressDescriptorSchema,
  ActionDescriptorSchema,
  ConfirmationDescriptorSchema,
  VoiceDescriptorSchema,
]);

export type UIDescriptor = z.infer<typeof UIDescriptorSchema>;
