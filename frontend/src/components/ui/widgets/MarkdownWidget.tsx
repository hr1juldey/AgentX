/**
 * Markdown widget for Real AgentX v0.1.
 *
 * Renders markdown content with flat design (C009).
 * Part of 12 frozen widget types from C007.
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { tokens } from '@/lib/design-tokens';

interface MarkdownWidgetProps {
  content: string;
  format?: 'markdown' | 'plain';
}

/**
 * Markdown widget component.
 *
 * Displays formatted markdown with flat styling (no gradients).
 * Follows C009 flat design guidelines.
 */
export function MarkdownWidget({ content, format = 'markdown' }: MarkdownWidgetProps) {
  return (
    <div
      className="bg-organelle border-b border-white/[0.06] rounded-lg p-organelle"
      style={{
        backgroundColor: tokens.color.cell,
        borderBottomColor: tokens.color.membrane,
      }}
    >
      {format === 'markdown' ? (
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown
            components={{
            h1: ({ children }) => (
              <h1 className="text-2xl font-bold text-nucleus mb-4 mt-0">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="text-xl font-semibold text-nucleus mb-3 mt-6">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="text-lg font-medium text-nucleus mb-2 mt-4">
                {children}
              </h3>
            ),
            p: ({ children }) => (
              <p className="text-base text-cytoplasm mb-4 leading-relaxed">
                {children}
              </p>
            ),
            code: ({ inline, children }: any) => (
              <code
                className={`${
                  inline
                    ? 'bg-membrane text-enzyme px-1 py-0.5 rounded text-sm'
                    : 'block bg-membrane text-enzyme p-4 rounded-lg my-4 text-sm overflow-x-auto'
                }`}
                style={{
                  backgroundColor: tokens.color.membrane,
                  color: tokens.color.enzyme,
                }}
              >
                {children}
              </code>
            ),
            ul: ({ children }) => (
              <ul className="list-disc list-inside text-cytoplasm space-y-1 mb-4">
                {children}
              </ul>
            ),
            ol: ({ children }) => (
              <ol className="list-decimal list-inside text-cytoplasm space-y-1 mb-4">
                {children}
              </ol>
            ),
            a: ({ href, children }) => (
              <a
                href={href}
                className="text-enzyme hover:underline"
                style={{ color: tokens.color.enzyme }}
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            ),
          }}
          >
            {content}
          </ReactMarkdown>
        </div>
      ) : (
        <p className="text-base text-cytoplasm whitespace-pre-wrap">{content}</p>
      )}
    </div>
  );
}
