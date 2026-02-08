/**
 * Library route constants for Design Library navigation.
 *
 * Single source of truth for all library-related routes.
 */

export const ROUTES = {
  LIBRARY: '/library',
  PHYSICS_CELLS: '/library/physics-cells',
  MORPHING_CENTRAL_ISLAND: '/library/morphing-central-island',
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
  {
    id: 'morphing-central-island',
    title: 'Morphing Central Island',
    description:
      'Morphing UI with biological metaphors - cell engulfing, cilia typing, metaball merging. A generative UI minimal surface.',
    slug: 'morphing-central-island',
    category: ComponentCategory.PHYSICS,
  },
];
