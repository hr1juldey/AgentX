/** WidgetCard component.
 *
 * Wrapper component for individual widgets with fade-in animation
 * and source attribution.
 */

import React, { useEffect, useState } from 'react';
import { WidgetSpecification } from '../types/widgets';

interface WidgetCardProps {
  widget: WidgetSpecification;
  index: number;
  visible: boolean;
}

// Type guard for array content
function isArray(value: unknown): value is unknown[] {
  return Array.isArray(value);
}

// Type guard for string array
function isStringArray(value: unknown): value is string[] {
  return isArray(value) && value.every((item) => typeof item === 'string');
}

export const WidgetCard: React.FC<WidgetCardProps> = ({
  widget,
  index,
  visible,
}) => {
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    if (visible) {
      // Small delay for staggered animation
      const timeout = setTimeout(() => setIsRevealed(true), index * 100);
      return () => clearTimeout(timeout);
    }
  }, [visible, index]);

  if (!visible) {
    return null;
  }

  return (
    <div
      className={`
        widget-card
        transition-all duration-500 ease-out
        ${isRevealed ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}
      `}
      style={{ transitionDelay: `${index * 100}ms` }}
    >
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 border border-gray-200 dark:border-gray-700">
        {/* Header with title and priority indicator */}
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
            {widget.title}
          </h3>
          <div
            className="text-xs px-2 py-1 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400"
            title={`Priority: ${widget.priority}/10`}
          >
            {widget.priority}
          </div>
        </div>

        {/* Widget content based on type */}
        <div className="widget-content">
          {renderWidgetContent(widget)}
        </div>

        {/* Source attribution */}
        {widget.sources.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Sources: {widget.sources.slice(0, 3).join(', ')}
              {widget.sources.length > 3 && ` +${widget.sources.length - 3} more`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

function renderWidgetContent(widget: WidgetSpecification): React.ReactNode {
  const { widget_type, content } = widget;

  switch (widget_type) {
    case 'text_card': {
      const text = typeof content.text === 'string' ? content.text : null;
      return (
        <div className="prose dark:prose-invert max-w-none">
          <p>{text || 'No content available.'}</p>
        </div>
      );
    }

    case 'data_table': {
      const headers = isStringArray(content.headers)
        ? content.headers
        : ['Column 1', 'Column 2'];
      const rows = isArray(content.rows) ? content.rows : [];

      return (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                {headers.map((header: string, i: number) => (
                  <th
                    key={i}
                    className="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {rows.map((row: unknown, i: number) => (
                <tr key={i}>
                  {isStringArray(row)
                    ? row.map((cell: string, j: number) => (
                        <td
                          key={j}
                          className="px-4 py-2 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                        >
                          {cell}
                        </td>
                      ))
                    : null}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    case 'timeline': {
      const events = isArray(content.events) ? content.events : [];
      return (
        <div className="space-y-3">
          {events.map((event: unknown, i: number) => {
            if (
              typeof event === 'object' &&
              event !== null &&
              'date' in event &&
              'description' in event
            ) {
              return (
                <div key={i} className="flex items-start space-x-3">
                  <div className="flex-shrink-0 w-2 h-2 mt-2 bg-blue-500 rounded-full" />
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                      {typeof event.date === 'string' ? event.date : 'Unknown date'}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {typeof event.description === 'string'
                        ? event.description
                        : 'No description'}
                    </p>
                  </div>
                </div>
              );
            }
            return null;
          })}
        </div>
      );
    }

    case 'chart': {
      const chartType = typeof content.chart_type === 'string' ? content.chart_type : 'unknown';
      return (
        <div className="h-48 flex items-center justify-center bg-gray-50 dark:bg-gray-900 rounded">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Chart visualization ({chartType})
          </p>
        </div>
      );
    }

    case 'map': {
      const locationCount = typeof content.location_count === 'number' ? content.location_count : 0;
      return (
        <div className="h-48 flex items-center justify-center bg-gray-50 dark:bg-gray-900 rounded">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Map visualization ({locationCount} locations)
          </p>
        </div>
      );
    }

    default:
      return <p className="text-sm text-gray-500">Unknown widget type</p>;
  }
}
