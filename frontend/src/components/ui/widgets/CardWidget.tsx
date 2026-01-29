/**
 * Card widget for Real AgentX v0.1.
 *
 * Displays content in a card with optional actions.
 * Part of 12 frozen widget types from C007.
 */

import React from 'react';
import { tokens } from '@/lib/design-tokens';

interface CardWidgetProps {
  title: string;
  content: string;
  actions?: Array<{
    label: string;
    action: string;
    primary?: boolean;
  }>;
}

/**
 * Card widget component.
 *
 * Displays content with flat styling (no gradients per C009).
 * Uses single accent color (enzyme/cyan) for actions.
 */
export function CardWidget({ title, content, actions = [] }: CardWidgetProps) {
  return (
    <div
      className="rounded-lg p-organelle"
      style={{
        backgroundColor: tokens.color.cell,
        borderBottom: `1px solid ${tokens.color.membrane}`,
      }}
    >
      {/* Title with flat design (no gradient) */}
      <h3 className="text-lg font-semibold mb-3" style={{ color: tokens.color.nucleus }}>
        {title}
      </h3>

      {/* Content */}
      <p className="text-base text-cytoplasm mb-4 leading-relaxed">{content}</p>

      {/* Actions with single accent color */}
      {actions.length > 0 && (
        <div className="flex gap-2">
          {actions.map((action, index) => (
            <button
              key={index}
              className={`px-4 py-2 rounded-lg font-medium transition-opacity hover:opacity-90 ${
                action.primary ? 'text-void' : 'text-nucleus'
              }`}
              style={{
                backgroundColor: action.primary
                  ? tokens.color.enzyme
                  : tokens.color.membrane,
                color: action.primary ? tokens.color.void : tokens.color.nucleus,
              }}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
