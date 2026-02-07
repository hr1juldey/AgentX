/**
 * Library index page - component showcase grid.
 *
 * Displays all available library components as cards with thumbnails.
 *
 * @see openspec/changes/physics-based-cell-division-voice/specs/library-index
 */

import Link from 'next/link';
import { LibraryHeader } from '@/components/layout/library-header';
import { LIBRARY_COMPONENTS } from '@/lib/navigation/library-routes';
import Image from 'next/image';

/**
 * Component card props.
 */
interface ComponentCardProps {
  title: string;
  description: string;
  thumbnail: string;
  slug: string;
}

/**
 * Component card.
 */
function ComponentCard({ title, description, thumbnail, slug }: ComponentCardProps) {
  return (
    <Link href={`/library/${slug}`} className="group">
      <div className="card overflow-hidden hover:shadow-lg hover:shadow-enzyme/10 transition-all duration-300 h-full">
        {/* Thumbnail */}
        <div className="relative aspect-video bg-gradient-to-br from-enzyme/20 to-microtubule/20 rounded-t-lg overflow-hidden">
          {thumbnail ? (
            <Image
              src={thumbnail}
              alt={title}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
            />
          ) : (
            <div className="flex items-center justify-center h-full text-cytoplasm">
              <span className="text-4xl opacity-50">🎨</span>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          <h3 className="text-heading mb-2 group-hover:text-enzyme transition-colors">
            {title}
          </h3>
          <p className="text-body text-cytoplasm mb-4 line-clamp-2">{description}</p>

          {/* View Demo button */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all text-enzyme group-hover:bg-enzyme/10">
            View Demo →
          </div>
        </div>
      </div>
    </Link>
  );
}

/**
 * Library index page component.
 */
export default function LibraryPage() {
  return (
    <main className="min-h-screen bg-void text-nucleus">
      <LibraryHeader />

      <div className="pt-24 px-6 pb-12">
        <div className="max-w-6xl mx-auto">
          {/* Page header */}
          <div className="mb-12">
            <h1 className="text-display mb-4">Design Library</h1>
            <p className="text-subheading text-cytoplasm">
              Explore experimental UI components with interactive demos.
            </p>
          </div>

          {/* Component grid */}
          {LIBRARY_COMPONENTS.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {LIBRARY_COMPONENTS.map((component) => (
                <ComponentCard
                  key={component.id}
                  title={component.title}
                  description={component.description}
                  thumbnail={component.thumbnail}
                  slug={component.slug}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📦</div>
              <h2 className="text-heading text-nucleus mb-2">No components yet</h2>
              <p className="text-body text-cytoplasm">Components will be added soon.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
