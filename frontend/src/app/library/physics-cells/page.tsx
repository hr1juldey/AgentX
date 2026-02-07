/**
 * Physics Cells demo page - isolated component demo.
 *
 * Full-viewport demo of the Physics Cells voice component with description and controls.
 *
 * @see openspec/changes/physics-based-cell-division-voice/specs/component-demo-page
 */

'use client';

import { useState } from 'react';
import { LibraryHeader } from '@/components/layout/library-header';
import { PhysicsCellsVoice } from '@/components/physics-cells-voice';
import { ColorSchemeWrapper } from '@/components/physics-cells/color-scheme-wrapper';

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
  const [cellCount, setCellCount] = useState(8);
  const [blur, setBlur] = useState(16);
  const [debug, setDebug] = useState(false);
  const [energyGain, setEnergyGain] = useState(0.05);
  const [energyDecay, setEnergyDecay] = useState(0.98);
  const [audioThresholdSlider, setAudioThresholdSlider] = useState(69); // ~120 dB
  const [baseDistance, setBaseDistance] = useState(0.15);
  const [maxDistance, setMaxDistance] = useState(2.5);
  const [viscousAdhesion, setViscousAdhesion] = useState(0.0);
  const [colorScheme, setColorScheme] = useState('ai');

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
