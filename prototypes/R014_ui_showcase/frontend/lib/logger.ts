// Unified logging service for AgentX frontend
// Provides consistent logging across the application with category-based filtering

/**
 * Log levels for categorizing log messages
 */
export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error'
}

/**
 * Logger interface - defines the logging API
 */
interface LoggerInterface {
  debug(category: string, message: string, data?: unknown): void;
  info(category: string, message: string, data?: unknown): void;
  warn(category: string, message: string, data?: unknown): void;
  error(category: string, message: string, data?: unknown): void;
  widget(message: string, data?: unknown): void;
  websocket(message: string, data?: unknown): void;
  render(message: string, data?: unknown): void;
  api(message: string, data?: unknown): void;
}

/**
 * Unified logger implementation
 *
 * Usage:
 *   logger.widget("Widget added:", { id: "abc" });
 *   logger.websocket("Connected:", { url: "ws://..." });
 *   logger.render("Component rendered:", { component: "HomePage" });
 *   logger.api("API call:", { endpoint: "/api/v1/health" });
 */
export const logger: LoggerInterface = {
  debug: (category: string, message: string, data?: unknown) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[${category.toUpperCase()}]`, message, data || '');
    }
  },

  info: (category: string, message: string, data?: unknown) => {
    console.log(`[${category.toUpperCase()}]`, message, data || '');
  },

  warn: (category: string, message: string, data?: unknown) => {
    console.warn(`[${category.toUpperCase()}]`, message, data || '');
  },

  error: (category: string, message: string, data?: unknown) => {
    console.error(`[${category.toUpperCase()}]`, message, data || '');
  },

  // Category-specific shortcuts for common logging scenarios
  widget: (message: string, data?: unknown) => {
    logger.debug('widget', message, data);
  },

  websocket: (message: string, data?: unknown) => {
    logger.debug('websocket', message, data);
  },

  render: (message: string, data?: unknown) => {
    logger.debug('render', message, data);
  },

  api: (message: string, data?: unknown) => {
    logger.debug('api', message, data);
  },
};

/**
 * Export a singleton instance for easy importing
 * Usage: import { logger } from '@/lib/logger';
 */
export default logger;
