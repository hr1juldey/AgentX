// EXTRACTED from app/page.tsx
// Constants for widgets and API configuration

/**
 * API configuration
 */
export const API_CONFIG = {
  URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8014",
  APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || "R014 UI Showcase",
} as const;

/**
 * Interaction configuration
 */
export const INTERACTION_CONFIG = {
  CLICK_THRESHOLD: 5,
} as const;
