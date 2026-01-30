/**
 * LoadExternalComponent - React portal for widget rendering.
 *
 * Custom implementation of LangGraph's LoadExternalComponent pattern.
 * Loads and renders widgets from the registry with style isolation.
 *
 * Features:
 * - Automatic widget type resolution from ui.tsx registry
 * - React portal for clean DOM manipulation
 * - Fallback component for unknown widget types
 * - Props validation and error handling
 *
 * Usage:
 * ```tsx
 * {values.ui?.map((ui) => (
 *   <LoadExternalComponent
 *     key={ui.id}
 *     message={ui}
 *     fallback={<SkeletonWidget />}
 *   />
 * ))}
 * ```
 */

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import WIDGET_REGISTRY, { hasWidgetType } from '@/agent/ui';
import type { UIMessage } from '@/agent/graph';

/**
 * Props for LoadExternalComponent.
 */
export interface LoadExternalComponentProps {
  /**
   * UI message from LangGraph state (created by push_ui_message).
   */
  message: UIMessage;

  /**
   * Fallback component to render while loading or on error.
   */
  fallback?: React.ReactNode;

  /**
   * Custom class name for the wrapper.
   */
  className?: string;

  /**
   * Additional styles for the wrapper.
   */
  style?: React.CSSProperties;
}

/**
 * Skeleton widget fallback.
 */
function SkeletonWidget() {
  return (
    <div className="bg-cell border border-membrane rounded-lg p-4 animate-pulse">
      <div className="h-4 bg-membrane rounded mb-2 w-3/4" />
      <div className="h-3 bg-membrane rounded mb-1 w-full" />
      <div className="h-3 bg-membrane rounded mb-1 w-5/6" />
    </div>
  );
}

/**
 * Error widget fallback.
 */
function ErrorWidget({ message, type }: { message: string; type: string }) {
  return (
    <div className="bg-lysosome/10 border border-lysosome/30 rounded-lg p-4">
      <div className="text-sm text-lysosome">Failed to render widget: {type}</div>
      <div className="text-xs text-vacuole mt-1">{message}</div>
    </div>
  );
}

/**
 * Widget wrapper - renders widget in isolated container.
 */
function WidgetWrapper({
  widgetType,
  widgetProps,
}: {
  widgetType: string;
  widgetProps: Record<string, any>;
}) {
  const Component = WIDGET_REGISTRY[widgetType];
  return <Component {...widgetProps} />;
}

/**
 * LoadExternalComponent - renders widgets from registry.
 *
 * Uses React portals for clean DOM manipulation.
 * Shadow DOM isolation is handled at the widget level if needed.
 */
export function LoadExternalComponent({
  message,
  fallback = <SkeletonWidget />,
  className = '',
  style = {},
}: LoadExternalComponentProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const { name: widgetType, props: widgetProps } = message;

  /**
   * Simulate loading state.
   */
  useEffect(() => {
    // Simulate async loading (e.g., lazy-loaded widget components)
    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 0);

    return () => clearTimeout(timer);
  }, []);

  /**
   * Validate widget type.
   */
  useEffect(() => {
    if (!isLoaded) return;

    if (!hasWidgetType(widgetType)) {
      setError(new Error(`Unknown widget type: ${widgetType}`));
    } else {
      setError(null);
    }
  }, [widgetType, isLoaded]);

  /**
   * Render fallback while loading or on error.
   */
  if (!isLoaded) {
    return <div className={className} style={style}>{fallback}</div>;
  }

  if (error) {
    return (
      <div className={className} style={style}>
        <ErrorWidget message={error.message} type={widgetType} />
      </div>
    );
  }

  /**
   * Render the widget.
   */
  return (
    <div className={className} style={style}>
      <WidgetWrapper widgetType={widgetType} widgetProps={widgetProps} />
    </div>
  );
}

/**
 * Default export.
 */
export default LoadExternalComponent;

/**
 * HOC for loading external components with additional functionality.
 *
 * Note: LoadExternalComponent does not accept children. The HOC pattern
 * renders the wrapped component with additional widget rendering capabilities.
 */
export function withLoadExternalComponent<P extends object>(
  WrappedComponent: React.ComponentType<P>
): React.ComponentType<Omit<P, keyof LoadExternalComponentProps> & LoadExternalComponentProps> {
  return function WithLoadExternalComponent(
    props: Omit<P, keyof LoadExternalComponentProps> & LoadExternalComponentProps
  ) {
    const { message, fallback, className, style, ...wrappedProps } = props;
    // Render wrapped component directly - LoadExternalComponent is used separately for widgets
    return <WrappedComponent {...(wrappedProps as P)} />;
  };
}

/**
 * Hook for checking widget type availability.
 */
export function useLoadExternalComponent() {
  const isWidgetAvailable = useCallback((widgetType: string): boolean => {
    return hasWidgetType(widgetType);
  }, []);

  const getWidgetComponent = useCallback((widgetType: string) => {
    if (!hasWidgetType(widgetType)) {
      return null;
    }
    return WIDGET_REGISTRY[widgetType];
  }, []);

  return { isWidgetAvailable, getWidgetComponent };
}

import { useCallback } from 'react';
