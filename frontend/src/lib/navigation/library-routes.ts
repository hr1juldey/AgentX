/**
 * Library route constants for Design Library navigation.
 *
 * Single source of truth for all library-related routes.
 */

export const ROUTES = {
  LIBRARY: '/library',
  PHYSICS_CELLS: '/library/physics-cells',
} as const;

/**
 * Library component metadata array.
 * Add new components here to appear in library index.
 */
import { LibraryComponent, ComponentCategory } from '@/types/library';

export const LIBRARY_COMPONENTS: LibraryComponent[] = [
  {
    id: 'physics-cells',
    title: 'Physics Cells',
    description:
      'Audio-reactive cell division with physics-based orbit mechanics. Speaking splits cells apart, silence merges them back.',
    slug: 'physics-cells',
    category: ComponentCategory.PHYSICS,
  },
];
