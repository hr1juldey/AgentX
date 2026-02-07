/**
 * Library component types for Design Library system.
 *
 * Defines metadata and structure for component showcase library.
 */

/**
 * Component category for filtering library items.
 */
export enum ComponentCategory {
  PHYSICS = 'physics',
  VOICE = 'voice',
  ANIMATION = 'animation',
  UI = 'ui',
}

/**
 * Library component metadata.
 * Used for component cards in library index.
 */
export interface LibraryComponent {
  id: string;
  title: string;
  description: string;
  thumbnail: string;
  slug: string;
  category: ComponentCategory;
}
