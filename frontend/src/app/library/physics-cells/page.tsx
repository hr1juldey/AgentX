/**
 * Physics Cells demo page - isolated component demo.
 *
 * Full-viewport demo of the Physics Cells voice component with description and controls.
 *
 * @see openspec/changes/physics-based-cell-division-voice/specs/component-demo-page
 */

'use client';

import { useState, useEffect } from 'react';
import { LibraryHeader } from '@/components/layout/library-header';
import { PhysicsCellsVoice } from '@/components/physics-cells-voice';
import { ColorSchemeWrapper } from '@/components/physics-cells/color-scheme-wrapper';

/**
 * localStorage key for physics cells settings.
 */
const PHYSICS_SETTINGS_KEY = 'physics-cells-settings';

/**
 * Default physics settings.
 */
const DEFAULT_SETTINGS = {
  cellCount: 8,
  blur: 16,
  debug: false,
  energyGain: 0.05,
  energyDecay: 0.98,
  audioThresholdSlider: 69,
  baseDistance: 0.15,
  maxDistance: 2.5,
  viscousAdhesion: 0.80,
  colorScheme: 'ai',
};

/**
 * Demo container component.
 */
function DemoContainer({
  title,
  description,
  children,
  controls,
  colorControls,
  scheme,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
  controls?: React.ReactNode;
  colorControls?: React.ReactNode;
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

          {/* Demo area - apply scheme wrapper here */}
          <div className="relative rounded-2xl overflow-hidden border border-membrane mb-6 bg-cell/50" style={{ height: '60vh' }}>
            <ColorSchemeWrapper scheme={scheme || 'custom'}>
              {children}
            </ColorSchemeWrapper>
          </div>

          {/* Color control panel */}
          {colorControls && (
            <div className="card mb-6">
              <h2 className="text-heading mb-4">🎨 Color Schemes (Raycast-Inspired)</h2>
              {colorControls}
            </div>
          )}

          {/* Physics control panel */}
          {controls && (
            <div className="card">
              <h2 className="text-heading mb-4">Physics Controls</h2>
              {controls}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Physics Cells demo page component.
 */
export default function PhysicsCellsDemoPage() {
  // Track if we're on client side (after mount)
  const [isClient, setIsClient] = useState(false);

  // Initialize all state with defaults first (SSR-safe)
  const [cellCount, setCellCount] = useState(DEFAULT_SETTINGS.cellCount);
  const [blur, setBlur] = useState(DEFAULT_SETTINGS.blur);
  const [debug, setDebug] = useState(DEFAULT_SETTINGS.debug);
  const [energyGain, setEnergyGain] = useState(DEFAULT_SETTINGS.energyGain);
  const [energyDecay, setEnergyDecay] = useState(DEFAULT_SETTINGS.energyDecay);
  const [audioThresholdSlider, setAudioThresholdSlider] = useState(DEFAULT_SETTINGS.audioThresholdSlider);
  const [baseDistance, setBaseDistance] = useState(DEFAULT_SETTINGS.baseDistance);
  const [maxDistance, setMaxDistance] = useState(DEFAULT_SETTINGS.maxDistance);
  const [viscousAdhesion, setViscousAdhesion] = useState(DEFAULT_SETTINGS.viscousAdhesion);
  const [colorScheme, setColorScheme] = useState(DEFAULT_SETTINGS.colorScheme);

  // Load from localStorage only on client side after mount
  useEffect(() => {
    if (typeof window === 'undefined') return;

    setIsClient(true);

    const saved = localStorage.getItem(PHYSICS_SETTINGS_KEY);
    if (saved) {
      try {
        const settings = JSON.parse(saved);
        if (settings.cellCount !== undefined) setCellCount(settings.cellCount);
        if (settings.blur !== undefined) setBlur(settings.blur);
        if (settings.debug !== undefined) setDebug(settings.debug);
        if (settings.energyGain !== undefined) setEnergyGain(settings.energyGain);
        if (settings.energyDecay !== undefined) setEnergyDecay(settings.energyDecay);
        if (settings.audioThresholdSlider !== undefined) setAudioThresholdSlider(settings.audioThresholdSlider);
        if (settings.baseDistance !== undefined) setBaseDistance(settings.baseDistance);
        if (settings.maxDistance !== undefined) setMaxDistance(settings.maxDistance);
        if (settings.viscousAdhesion !== undefined) setViscousAdhesion(settings.viscousAdhesion);
        if (settings.colorScheme !== undefined) setColorScheme(settings.colorScheme);
      } catch (e) {
        console.error('Failed to parse saved settings:', e);
      }
    }
  }, []);

  // Save all settings to localStorage whenever any value changes (after mount)
  useEffect(() => {
    if (!isClient || typeof window === 'undefined') return;
    const settings = {
      cellCount,
      blur,
      debug,
      energyGain,
      energyDecay,
      audioThresholdSlider,
      baseDistance,
      maxDistance,
      viscousAdhesion,
      colorScheme,
    };
    localStorage.setItem(PHYSICS_SETTINGS_KEY, JSON.stringify(settings));
  }, [isClient, cellCount, blur, debug, energyGain, energyDecay, audioThresholdSlider, baseDistance, maxDistance, viscousAdhesion, colorScheme]);

  // Logarithmic mapping: slider (1-100) → threshold (1-1000, dB-like scale)
  const audioThreshold = Math.round(Math.pow(10, (audioThresholdSlider * 3 / 100)));

  const description = `Audio-reactive cell division with physics-based orbit mechanics.

• Speaking splits cells apart
• Silence merges them back together
• Energy accumulation physics with spring damping
• 4-12 orbiting cells around central nucleus

Enable the microphone to see audio reactivity, or use debug mode to visualize the energy state.`;

  // Force recompilation
  return (
    <DemoContainer
      title="Physics Cells"
      description={description}
      scheme={colorScheme}
      colorControls={
        <div className="space-y-6">
          {/* Scheme buttons */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <button
              onClick={() => setColorScheme('raycast')}
              className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                colorScheme === 'raycast'
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'bg-white/5 text-white/70 hover:bg-white/10'
              }`}
            >
              Raycast
            </button>
            <button
              onClick={() => setColorScheme('ai')}
              className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                colorScheme === 'ai'
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'bg-white/5 text-white/70 hover:bg-white/10'
              }`}
            >
              AI Assistant
            </button>
            <button
              onClick={() => setColorScheme('warm')}
              className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                colorScheme === 'warm'
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'bg-white/5 text-white/70 hover:bg-white/10'
              }`}
            >
              Warm
            </button>
            <button
              onClick={() => setColorScheme('minimal')}
              className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                colorScheme === 'minimal'
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'bg-white/5 text-white/70 hover:bg-white/10'
              }`}
            >
              Minimal
            </button>
            <button
              onClick={() => setColorScheme('custom')}
              className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                colorScheme === 'custom'
                  ? 'bg-white/20 text-white ring-2 ring-white/40'
                  : 'bg-white/5 text-white/70 hover:bg-white/10'
              }`}
            >
              Custom
            </button>
          </div>

          {/* Current scheme info */}
          <div className="flex items-center gap-4 text-sm text-white/50">
            <span>Current scheme: <strong className="text-white/80">{colorScheme}</strong></span>
            <span className="text-white/30">|</span>
            <span>Background: <span style={{color: 'var(--scheme-nucleus-active)'}}>Accent colors from CSS variables</span></span>
          </div>
        </div>
      }
      controls={
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Cell count slider */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Cell Count: {cellCount}
            </label>
            <input
              type="range"
              min={4}
              max={12}
              value={cellCount}
              onChange={(e) => setCellCount(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Blur slider */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Blur Amount: {blur}
            </label>
            <input
              type="range"
              min={8}
              max={24}
              value={blur}
              onChange={(e) => setBlur(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Debug toggle */}
          <div className="flex items-center">
            <button
              onClick={() => setDebug(!debug)}
              className={`btn ${debug ? 'btn-primary' : 'btn-secondary'}`}
            >
              {debug ? 'Debug ON' : 'Debug OFF'}
            </button>
          </div>

          {/* Energy Gain Rate */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Energy Gain: {energyGain.toFixed(2)} (higher = more sensitive)
            </label>
            <input
              type="range"
              min={0.01}
              max={1.0}
              step={0.01}
              value={energyGain}
              onChange={(e) => setEnergyGain(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Energy Decay Rate */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Energy Decay: {energyDecay.toFixed(2)} (higher = slower fade)
            </label>
            <input
              type="range"
              min={0.50}
              max={0.99}
              step={0.01}
              value={energyDecay}
              onChange={(e) => setEnergyDecay(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Audio Threshold */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Audio Threshold: {audioThreshold} dB (logarithmic, lower = more sensitive)
            </label>
            <input
              type="range"
              min={1}
              max={100}
              value={audioThresholdSlider}
              onChange={(e) => setAudioThresholdSlider(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Base Distance */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Base Distance: {baseDistance.toFixed(2)} (starting position)
            </label>
            <input
              type="range"
              min={0.1}
              max={1.0}
              step={0.01}
              value={baseDistance}
              onChange={(e) => setBaseDistance(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Max Distance */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Max Distance: {maxDistance.toFixed(2)} (max expansion)
            </label>
            <input
              type="range"
              min={1.0}
              max={5.0}
              step={0.1}
              value={maxDistance}
              onChange={(e) => setMaxDistance(Number(e.target.value))}
              className="w-full"
            />
          </div>

          {/* Viscous Adhesion */}
          <div>
            <label className="block text-caption mb-2 text-cytoplasm">
              Viscous Adhesion: {viscousAdhesion.toFixed(2)} (friction when returning)
            </label>
            <input
              type="range"
              min={0.0}
              max={1.0}
              step={0.05}
              value={viscousAdhesion}
              onChange={(e) => setViscousAdhesion(Number(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
      }
    >
      <PhysicsCellsVoice
        cellCount={cellCount}
        blur={blur}
        debug={debug}
        enableMic={true}
        nucleusRadius={160}
        energyGainRate={energyGain}
        energyDecayRate={energyDecay}
        audioThreshold={audioThreshold}
        baseDistance={baseDistance}
        maxDistance={maxDistance}
        viscousAdhesion={viscousAdhesion}
        useSchemeColors={true}
      />
    </DemoContainer>
  );
}
