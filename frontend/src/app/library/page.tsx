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
import { lazy, Suspense } from 'react';

/**
 * Component card props.
 */
interface ComponentCardProps {
  id: string;
  title: string;
  description: string;
  slug: string;
}

/**
 * Live preview component props.
 */
interface LivePreviewProps {
  componentId: string;
}

/**
 * Live thumbnail preview - renders mini version of component.
 *
 * Dynamically imports the component based on ID and renders
 * a scaled-down preview without audio/mic interaction.
 */
function LivePreview({ componentId }: LivePreviewProps) {
  // Map component IDs to their preview components
  const previewComponents: Record<string, React.LazyExoticComponent<React.ComponentType<any>>> = {
    'physics-cells': lazy(() =>
      import('@/components/physics-cells-voice').then((mod) => ({
        default: () => {
          const PhysicsCellsVoice = mod.PhysicsCellsVoice;
          return (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-enzyme/20 to-microtubule/20">
              <PhysicsCellsVoice
                cellCount={6}
                blur={12}
                nucleusRadius={48}
                enableMic={false}
                debug={false}
                energyGainRate={0.3}
                energyDecayRate={0.96}
                audioThreshold={50}
                baseDistance={0.2}
                maxDistance={0.8}
                viscousAdhesion={0.3}
                useSchemeColors={true}
              />
            </div>
          );
        },
      }))
    ),
    'morphing-central-island': lazy(() =>
      import('@/components/central-island/nucleus').then((mod) => ({
        default: () => {
          const Nucleus = mod.Nucleus;
          return (
            <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-enzyme/20 to-microtubule/20">
              <div className="relative scale-75">
                <Nucleus state="idle" interactive={false} colorScheme="ai" />
                {/* Decorative mode islands (static for preview) */}
                <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
                  <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-12 h-12 rounded-full bg-[#A78BFA] opacity-60 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/></svg>
                  </div>
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-20 w-12 h-12 rounded-full bg-[#6366F1] opacity-60 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                  </div>
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-20 w-12 h-12 rounded-full bg-[#22D3EE] opacity-60 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
                  </div>
                  <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 translate-y-20 w-12 h-12 rounded-full bg-[#EC4899] opacity-60 flex items-center justify-center">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2"><path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/></svg>
                  </div>
                </div>
              </div>
            </div>
          );
        },
      }))
    ),
  };

  const PreviewComponent = previewComponents[componentId];

  if (!PreviewComponent) {
    return (
      <div className="w-full h-full flex items-center justify-center text-cytoplasm">
        <span className="text-4xl opacity-50">🎨</span>
      </div>
    );
  }

  return (
    <Suspense
      fallback={
        <div className="w-full h-full flex items-center justify-center text-cytoplasm">
          <div className="animate-pulse text-sm">Loading...</div>
        </div>
      }
    >
      <PreviewComponent />
    </Suspense>
  );
}

/**
 * Component card.
 */
function ComponentCard({ id, title, description, slug }: ComponentCardProps) {
  return (
    <Link href={`/library/${slug}`} className="group">
      <div className="card overflow-hidden hover:shadow-lg hover:shadow-enzyme/10 transition-all duration-300 h-full flex flex-col">
        {/* Live Preview Thumbnail */}
        <div className="relative aspect-video bg-gradient-to-br from-enzyme/20 to-microtubule/20 rounded-t-lg overflow-hidden">
          <LivePreview componentId={id} />

          {/* Overlay on hover */}
          <div className="absolute inset-0 bg-void/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
            <div className="px-4 py-2 bg-enzyme text-void rounded-lg text-sm font-medium">
              View Demo →
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 flex-1 flex flex-col">
          <h3 className="text-heading mb-2 group-hover:text-enzyme transition-colors">
            {title}
          </h3>
          <p className="text-body text-cytoplasm mb-4 line-clamp-2 flex-1">{description}</p>

          {/* View Demo link */}
          <div className="inline-flex items-center gap-2 text-sm font-medium transition-all text-enzyme group-hover:text-enzyme/80">
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
                  id={component.id}
                  title={component.title}
                  description={component.description}
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
