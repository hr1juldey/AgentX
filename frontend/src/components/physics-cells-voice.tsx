/**
 * Physics-based cell division voice component.
 *
 * Audio-reactive cells that split apart when speaking and merge back in silence.
 * Uses energy accumulation physics with spring damping and orbit mechanics.
 *
 * @see openspec/changes/physics-based-cell-division-voice/specs
 */

'use client';

import { useEffect, useState, useRef } from 'react';
import { usePhysicsCells } from '@/lib/physics/usePhysicsCells';
import { polarToCartesian } from '@/lib/physics/orbit-physics';

/**
 * Component configuration props.
 */
export interface PhysicsCellsVoiceProps {
  /** Number of orbiting cells (4-12) */
  cellCount?: number;
  /** Blur amount for metaball effect */
  blur?: number;
  /** Nucleus radius (desktop) */
  nucleusRadius?: number;
  /** Show debug energy bar */
  debug?: boolean;
  /** Enable microphone input */
  enableMic?: boolean;
  /** Audio level callback (optional) */
  onAudioLevel?: (level: number) => void;
  /** Energy gain rate - higher = more sensitive (0.01-1.0) */
  energyGainRate?: number;
  /** Energy decay rate - higher = slower decay (0.90-0.99) */
  energyDecayRate?: number;
  /** Audio threshold - lower = more sensitive (1-100) */
  audioThreshold?: number;
  /** Base distance - cells start here (0.05-0.5) */
  baseDistance?: number;
  /** Max distance - cells expand to here (0.5-2.0) */
  maxDistance?: number;
  /** Viscous adhesion - friction when returning to base (0.0-1.0) */
  viscousAdhesion?: number;
  /** Use CSS variables for colors from color scheme */
  useSchemeColors?: boolean;
}

/**
 * Physics-based cell division voice component.
 */
export function PhysicsCellsVoice({
  cellCount = 8,
  blur = 16,
  nucleusRadius = 160,
  debug = false,
  enableMic = true,
  onAudioLevel,
  energyGainRate = 0.3,
  energyDecayRate = 0.98,
  audioThreshold = 30,
  baseDistance = 0.15,
  maxDistance = 0.75,
  viscousAdhesion = 0.0,
  useSchemeColors = false,
}: PhysicsCellsVoiceProps) {
  const [micEnabled, setMicEnabled] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);

  // Debug: log props to verify cellCount is received
  if (debug && process.env.NODE_ENV === 'development') {
    console.log(`[PhysicsCellsVoice] Props received - cellCount: ${cellCount}, blur: ${blur}, energyGainRate: ${energyGainRate}, useSchemeColors: ${useSchemeColors}`);
  }

  // Physics hook
  const { cells, energy, maxDistance: maxDist, setAudioLevel: setPhysicsAudioLevel, start } = usePhysicsCells({
    cellCount,
    baseDistance,
    maxDistance,
    energyGainRate,
    energyDecayRate,
    viscousAdhesion,
  });

  // Debug: log actual cells array
  if (debug && process.env.NODE_ENV === 'development' && Math.random() < 0.02) {
    console.log(`[PhysicsCellsVoice] State - cells.length: ${cells.length}, energy: ${energy.toFixed(2)}`);
  }

  // Audio refs
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);
  const audioThresholdRef = useRef(audioThreshold);
  const debugRef = useRef(debug);

  // Keep refs in sync with props
  useEffect(() => {
    audioThresholdRef.current = audioThreshold;
  }, [audioThreshold]);

  useEffect(() => {
    debugRef.current = debug;
  }, [debug]);

  // Start physics animation on mount
  useEffect(() => {
    start();
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [start]);

  // Set up audio analysis when mic is enabled
  useEffect(() => {
    if (!micEnabled || !enableMic) {
      setAudioLevel(0);
      setPhysicsAudioLevel(0);
      return;
    }

    let mounted = true;

    const setupAudio = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        if (!mounted) return;

        if (!audioContextRef.current) {
          audioContextRef.current = new AudioContext();
        }

        const audioContext = audioContextRef.current;
        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;

        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        // Calculate voice-relevant frequency bins (300-3400Hz)
        const sampleRate = audioContext.sampleRate;
        const binResolution = sampleRate / analyser.fftSize;  // Hz per bin
        const voiceMinBin = Math.floor(300 / binResolution);   // ~300Hz
        const voiceMaxBin = Math.ceil(3400 / binResolution);    // ~3400Hz
        const voiceBinCount = voiceMaxBin - voiceMinBin + 1;

        const analyzeAudio = () => {
          if (!mounted || !analyserRef.current) {
            setAudioLevel(0);
            setPhysicsAudioLevel(0);
            return;
          }

          analyserRef.current.getByteFrequencyData(dataArray);

          // Sum only voice-relevant frequencies (300-3400Hz)
          let sum = 0;
          for (let i = voiceMinBin; i <= voiceMaxBin; i++) {
            sum += dataArray[i];
          }
          const average = sum / voiceBinCount;
          const currentThreshold = audioThresholdRef.current;
          const currentDebug = debugRef.current;

          // Noise gate: sounds below threshold produce ZERO energy
          let normalizedLevel = 0;
          if (average >= currentThreshold) {
            // Only sounds above threshold contribute (scaled relative to threshold)
            normalizedLevel = Math.min((average - currentThreshold) / currentThreshold, 1);
          }

          // Debug: log audio levels every 30 frames
          if (currentDebug && Math.random() < 0.03) {
            console.log(`[Audio Voice Band] raw: ${average.toFixed(1)}, threshold: ${currentThreshold}, gated: ${normalizedLevel.toFixed(2)}, bins: ${voiceMinBin}-${voiceMaxBin} (${voiceBinCount} bins for 300-3400Hz)`);
          }

          setAudioLevel(normalizedLevel);
          setPhysicsAudioLevel(normalizedLevel);
          onAudioLevel?.(normalizedLevel);

          animationRef.current = requestAnimationFrame(analyzeAudio);
        };

        animationRef.current = requestAnimationFrame(analyzeAudio);
      } catch (error) {
        console.error('[PhysicsCellsVoice] Failed to access microphone:', error);
        setMicEnabled(false);
      }
    };

    setupAudio();

    return () => {
      mounted = false;
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [micEnabled, enableMic, setPhysicsAudioLevel, onAudioLevel]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      audioContextRef.current?.close();
    };
  }, []);

  // Calculate viewbox size
  const padding = blur * 2;
  const maxOrbitRadius = (nucleusRadius / 2) * maxDist;
  const maxCellRadius = cells.length > 0 ? Math.max(...cells.map((c) => c.radius)) : 35;
  const viewBoxSize = nucleusRadius + padding * 2 + maxOrbitRadius + maxCellRadius * 2;
  const centerOffset = viewBoxSize / 2;

  return (
    <div className="relative" style={{ width: '100%', height: '100%', minHeight: '200px' }}>
      {/* Debug: Show cell count */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute top-2 left-2 text-xs text-cytoplasm z-50 pointer-events-none">
          Cells: {cells.length} | ViewBox: {Math.round(viewBoxSize)}
        </div>
      )}

      <svg
        className="w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <filter id={`goo-physics-cells-${cellCount}`}>
            <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
              result="goo"
            />
          </filter>
          <style>
            {`
              @keyframes cellBreathing {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
              }
              @keyframes nucleusBreathing {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.05); }
              }
              .cell-breathe-${cellCount} {
                transform-box: fill-box;
                transform-origin: center;
                animation: cellBreathing 3s ease-in-out infinite;
              }
              .nucleus-breathe-${cellCount} {
                transform-box: fill-box;
                transform-origin: center;
                animation: nucleusBreathing 2.5s ease-in-out infinite;
              }
            `}
          </style>
        </defs>

        <g filter={`url(#goo-physics-cells-${cellCount})`}>
          {/* Orbiting cells */}
          {cells.map((cell, index) => {
            const orbitRadius = (nucleusRadius / 2) * cell.distance;
            const pos = polarToCartesian(cell.angle, orbitRadius, cell.radius);
            const x = centerOffset + pos.x;
            const y = centerOffset + pos.y;

            // Round all values to 2 decimal places to avoid floating point hydration mismatches
            const cellColor = useSchemeColors
              ? `var(--scheme-cell-${(index % 6) + 1}, ${cell.color})`
              : cell.color;

            return (
              <circle
                key={cell.id}
                cx={Math.round(x * 100) / 100}
                cy={Math.round(y * 100) / 100}
                r={Math.round(cell.radius * 100) / 100}
                fill={cellColor}
                opacity={0.85}
                className={`cell-breathe-${cellCount}`}
                style={{ animationDelay: `${index * 150}ms` }}
              />
            );
          })}

          {/* Nucleus */}
          <circle
            cx={Math.round(centerOffset * 100) / 100}
            cy={Math.round(centerOffset * 100) / 100}
            r={Math.round((nucleusRadius / 3.2) * 100) / 100}
            fill={
              useSchemeColors
                ? `var(--scheme-nucleus-${energy > 0.5 ? 'active' : 'inactive'}, ${energy > 0.5 ? '#00D9FF' : '#FF6B35'})`
                : energy > 0.5 ? '#00D9FF' : '#FF6B35'
            }
            className={`nucleus-breathe-${cellCount}`}
          />
        </g>
      </svg>

      {/* Debug energy bar */}
      {debug && (
        <div className="absolute bottom-0 left-0 right-0 p-2 bg-void/90 rounded-t-lg">
          <div className="w-full h-2 bg-membrane rounded-full overflow-hidden">
            <div
              className="h-full bg-enzyme transition-all duration-75"
              style={{ width: `${energy * 100}%` }}
            />
          </div>
          <div className="text-caption text-cytoplasm mt-1">
            Energy: {energy.toFixed(2)} | Audio: {audioLevel.toFixed(2)} | Threshold: {audioThreshold}
          </div>
        </div>
      )}

      {/* Mic toggle button */}
      {enableMic && (
        <button
          onClick={() => setMicEnabled(!micEnabled)}
          className={`absolute bottom-4 px-4 py-2 rounded-full text-caption font-medium transition-all ${
            micEnabled
              ? 'bg-enzyme text-void hover:opacity-90'
              : 'bg-membrane text-nucleus hover:bg-cell'
          }`}
        >
          {micEnabled ? 'Mic ON' : 'Enable Mic'}
        </button>
      )}
    </div>
  );
}
