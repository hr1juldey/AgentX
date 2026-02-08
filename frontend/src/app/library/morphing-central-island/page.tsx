/**
 * Morphing Central Island demo page.
 *
 * Demonstrates the morphing UI with biological metaphors:
 * - Longpress nucleus to spawn mode islands
 * - Mode selection triggers sequential collapse
 * - Voice/chat modes with cell widgets and cilia typing
 *
 * @see openspec/changes/morphing-central-island
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { LibraryHeader } from '@/components/layout/library-header';
import { Nucleus } from '@/components/central-island/nucleus';
import { ModeIslands, ModeType } from '@/components/central-island/mode-islands';
import { MetaballWrapper } from '@/components/central-island/metaball-wrapper';
import { useLongpress } from '@/lib/longpress/use-longpress';
import { ColorSchemeWrapper } from '@/components/physics-cells/color-scheme-wrapper';

const DEMO_SETTINGS_KEY = 'morphing-central-island-settings';

const DEFAULT_SETTINGS = {
  colorScheme: 'ai',
};

/**
 * Demo container with ColorSchemeWrapper for physics-cells colors.
 */
function DemoContainer({
  title,
  description,
  children,
  controls,
  scheme,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
  controls?: React.ReactNode;
  scheme?: string;
}) {
  return (
    <div className="min-h-screen bg-void text-nucleus">
      <LibraryHeader />

      <div className="pt-20 px-6 pb-12">
        <div className="max-w-6xl mx-auto">
          {/* Description section */}
          <div className="mb-8">
            <h1 className="text-display mb-4">{title}</h1>
            <p className="text-body text-cytoplasm whitespace-pre-line">{description}</p>
          </div>

          {/* Demo area */}
          <div className="relative rounded-2xl overflow-hidden border border-membrane mb-6 bg-cell/50" style={{ height: '70vh' }}>
            <ColorSchemeWrapper scheme={scheme || 'ai'}>
              {children}
            </ColorSchemeWrapper>
          </div>

          {/* Control panel */}
          {controls && (
            <div className="card">
              <h2 className="text-heading mb-4">Demo Controls</h2>
              {controls}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Main demo page component.
 */
export default function MorphingCentralIslandDemoPage() {
  const [isClient, setIsClient] = useState(false);
  const [colorScheme, setColorScheme] = useState(DEFAULT_SETTINGS.colorScheme);
  const [selectedMode, setSelectedMode] = useState<ModeType | null>(null);
  const [selectedModeCurrentPosition, setSelectedModeCurrentPosition] = useState<{ x: number; y: number } | null>(null);
  const [nucleusState, setNucleusState] = useState<'idle' | 'longpress' | 'mode-selected'>('idle');
  const [isCollapsing, setIsCollapsing] = useState(false);
  const [collapseProgress, setCollapseProgress] = useState(0);
  const [collapseComplete, setCollapseComplete] = useState(false);
  const [shouldShowIslands, setShouldShowIslands] = useState(false); // Control island visibility

  // Refs to track animation state
  const collapseAnimationRef = useRef<number | null>(null);
  const isCollapseAnimatingRef = useRef(false);

  // Mode colors from physics-cells scheme
  const modeColors = {
    voice: 'var(--scheme-cell-3, #A78BFA)',
    chat: 'var(--scheme-cell-2, #6366F1)',
    file: 'var(--scheme-cell-1, #22D3EE)',
    camera: 'var(--scheme-cell-5, #EC4899)',
  };

  // Mode positions relative to nucleus
  const modePositions = {
    voice: { x: 0, y: -80 },
    chat: { x: -80, y: 0 },
    file: { x: 80, y: 0 },
    camera: { x: 0, y: 80 },
  };

  const allModes: ModeType[] = ['voice', 'chat', 'file', 'camera'];

  // Load from localStorage on client
  useState(() => {
    setIsClient(true);
  });

  // Longpress hook
  const { isLongpressActive, longpressProgress, bind } = useLongpress({
    duration: 1500,
    hapticTime: 1000,
    onLongpress: () => {
      // Only spawn islands if we're not already in a completed state
      if (!collapseComplete && !selectedMode) {
        setNucleusState('longpress');
        setShouldShowIslands(true); // Show islands on longpress
      }
    },
    onCancel: () => {
      // Only return to idle if not in middle of collapse
      if (!isCollapsing && !collapseComplete) {
        setNucleusState('idle');
      }
    },
  });

  // Handle mode selection - now includes current position
  const handleModeSelect = (mode: ModeType, currentPosition: { x: number; y: number }) => {
    console.log(`[Demo] Mode selected: ${mode} at current position:`, currentPosition);
    setSelectedMode(mode);
    setSelectedModeCurrentPosition(currentPosition);
    setNucleusState('mode-selected');
    setIsCollapsing(true);
    setCollapseProgress(0);
  };

  // Animate collapse progress - two phases using refs for reliable tracking
  // Phase 1 (progress 0-1): Non-selected islands and nucleus collapse toward selected island
  // Phase 2 (progress 1-2): Selected island moves to center
  const startCollapseAnimation = useCallback(() => {
    if (isCollapseAnimatingRef.current || !selectedMode) {
      console.log('[Demo] Collapse animation already running or no mode selected');
      return;
    }

    isCollapseAnimatingRef.current = true;
    console.log('[Demo] Starting collapse animation for mode:', selectedMode);
    let startTime: number | null = null;

    const animateCollapse = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;

      // Phase 1: Collapse toward selected island (0-1 over 1 second)
      const phase1Progress = Math.min(elapsed / 1000, 1);
      setCollapseProgress(phase1Progress);

      console.log(`[Demo] Phase 1 progress: ${(phase1Progress * 100).toFixed(0)}%`);

      if (phase1Progress < 1) {
        collapseAnimationRef.current = requestAnimationFrame(animateCollapse);
      } else {
        // Phase 1 complete
        console.log('[Demo] Phase 1 complete - transitioning to Phase 2');

        // Update state for Phase 2
        setIsCollapsing(false);

        // Small delay to ensure state update propagates
        setTimeout(() => {
          setCollapseComplete(true);

          // Phase 2: Animate selected island to center (1-2 over 500ms)
          let phase2StartTime: number | null = null;
          const animatePhase2 = (timestamp: number) => {
            if (!phase2StartTime) phase2StartTime = timestamp;
            const phase2Elapsed = timestamp - phase2StartTime;

            // Progress from 1 to 2
            const phase2Progress = Math.min(phase2Elapsed / 500, 1);
            setCollapseProgress(1 + phase2Progress);

            console.log(`[Demo] Phase 2 progress: ${(phase2Progress * 100).toFixed(0)}%`);

            if (phase2Progress < 1) {
              collapseAnimationRef.current = requestAnimationFrame(animatePhase2);
            } else {
              console.log('[Demo] Complete animation finished - selected island at center');
              isCollapseAnimatingRef.current = false;
              setCollapseProgress(2); // Final state
            }
          };

          collapseAnimationRef.current = requestAnimationFrame(animatePhase2);
        }, 50);
      }
    };

    collapseAnimationRef.current = requestAnimationFrame(animateCollapse);
  }, [selectedMode]);

  // Trigger animation when collapsing starts
  useEffect(() => {
    if (isCollapsing && selectedMode && collapseProgress === 0) {
      startCollapseAnimation();
    }
  }, [isCollapsing, selectedMode, collapseProgress, startCollapseAnimation]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (collapseAnimationRef.current) {
        cancelAnimationFrame(collapseAnimationRef.current);
      }
    };
  }, []);

  // Reset to idle
  const handleReset = () => {
    console.log('[Demo] Resetting to idle');
    setSelectedMode(null);
    setSelectedModeCurrentPosition(null);
    setNucleusState('idle');
    setIsCollapsing(false);
    setCollapseComplete(false);
    setCollapseProgress(0);
    setShouldShowIslands(false); // Hide islands on reset
    isCollapseAnimatingRef.current = false; // Reset animation flag
  };

  // Handle collapse complete
  const handleCollapseComplete = () => {
    console.log('[Demo] Collapse complete');
    setIsCollapsing(false);
  };

  const description = `Morphing UI with biological metaphors - the Central Island.

• Longpress (1.5s) the nucleus to spawn 4 mode islands
• Select a mode to trigger sequential collapse
• Voice mode spawns functional widget cells
• Chat mode features biological typewriter with cilia

Current state: ${nucleusState}
${selectedMode ? `Selected mode: ${selectedMode}` : ''}
Longpress progress: ${(longpressProgress * 100).toFixed(0)}%`;

  return (
    <DemoContainer
      title="Morphing Central Island"
      description={description}
      scheme={colorScheme}
      controls={
        <div className="space-y-6">
          {/* Color scheme selector */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {(['raycast', 'ai', 'warm', 'minimal', 'custom'] as const).map((scheme) => (
              <button
                key={scheme}
                onClick={() => setColorScheme(scheme)}
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  colorScheme === scheme
                    ? 'bg-white/20 text-white ring-2 ring-white/40'
                    : 'bg-white/5 text-white/70 hover:bg-white/10'
                }`}
              >
                {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
              </button>
            ))}
          </div>

          {/* Debug info */}
          <div className="flex items-center gap-4 text-sm text-white/50">
            <span>Current scheme: <strong className="text-white/80">{colorScheme}</strong></span>
            <span className="text-white/30">|</span>
            <span>Nucleus state: <strong className="text-white/80">{nucleusState}</strong></span>
            <span className="text-white/30">|</span>
            <span>Progress: <strong className="text-white/80">{(longpressProgress * 100).toFixed(0)}%</strong></span>
          </div>

          {/* Reset button */}
          {selectedMode && (
            <button
              onClick={handleReset}
              className="btn btn-secondary"
            >
              Reset to Idle
            </button>
          )}
        </div>
      }
    >
      {/* Central Island demo */}
      <div className="relative w-full h-full">
        <MetaballWrapper id="metaball-central-island">
          {/* Mode Islands - spawns on longpress, collapses when mode selected */}
          {shouldShowIslands && (
            <ModeIslands
              key={`islands-${selectedMode || 'none'}`} // Force remount on mode change
              isLongpressActive={isLongpressActive}
              onModeSelect={handleModeSelect}
              colorScheme={colorScheme}
              isCollapsing={isCollapsing}
              selectedMode={selectedMode}
              collapseProgress={collapseProgress}
              collapseComplete={collapseComplete}
              shouldShowIslands={shouldShowIslands}
            />
          )}

          {/* Central Nucleus - main interaction point */}
          <Nucleus
            key={`nucleus-${nucleusState}`} // Force remount when state changes
            state={nucleusState}
            colorScheme={colorScheme}
            interactive={!selectedMode || collapseComplete} // Disable during collapse
            selectedMode={selectedMode}
            isCollapsing={isCollapsing}
            collapseProgress={collapseProgress}
            collapseComplete={collapseComplete}
            selectedModeCurrentPosition={selectedModeCurrentPosition}
            {...bind}
          />
        </MetaballWrapper>

        {/* Debug info overlay */}
        {process.env.NODE_ENV === 'development' && (
          <div className="absolute top-4 left-4 text-xs text-white/50 space-y-1 pointer-events-none">
            <div>Longpress Active: {isLongpressActive ? 'YES' : 'NO'}</div>
            <div>Longpress Progress: {(longpressProgress * 100).toFixed(0)}%</div>
            <div>Selected Mode: {selectedMode || 'none'}</div>
            {selectedModeCurrentPosition && (
              <div>Selected Mode Position: ({selectedModeCurrentPosition.x.toFixed(0)}, {selectedModeCurrentPosition.y.toFixed(0)})</div>
            )}
            <div>Is Collapsing: {isCollapsing ? 'YES' : 'NO'}</div>
            <div>Collapse Complete: {collapseComplete ? 'YES' : 'NO'}</div>
            <div>Collapse Progress: {collapseProgress.toFixed(2)}</div>
          </div>
        )}
      </div>
    </DemoContainer>
  );
}
