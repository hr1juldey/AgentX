/**
 * Organic UI voice nucleus button component (C008).
 *
 * Central voice interface component with metaball-based organic design.
 * Mobile: 72px radius
 * Desktop: 160px radius
 *
 * Uses SVG goo filter for fluid, organic merging effect.
 * Orbiting animated blobs merge with the nucleus.
 * Audio reactivity: Blobs pulse based on microphone input levels.
 *
 * @see agentx_organic_ui_design_system.md
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { tokens, motion } from '@/lib/design-tokens';
import { VoiceClient } from '@/lib/voice/client';
import { VoiceMessageType } from '@/lib/voice/types';

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

const BACKEND_WS_URL = process.env.NEXT_PUBLIC_BACKEND_WS_URL || 'ws://localhost:8015';

interface OrbitingBlob {
  id: number;
  angle: number;
  baseDistance: number;
  distance: number;
  baseRadius: number;
  radius: number;
  speed: number;
  phaseOffset: number;
  color: string;
}

/**
 * Voice nucleus button with organic metaball effect and audio reactivity.
 */
export function VoiceButton() {
  const [state, setState] = useState<VoiceState>('idle');
  const [platform, setPlatform] = useState<'mobile' | 'desktop'>('desktop');
  const [isConnected, setIsConnected] = useState(false);
  const [blobs, setBlobs] = useState<OrbitingBlob[]>([]);
  const [audioLevel, setAudioLevel] = useState(0);

  const voiceClientRef = useRef<VoiceClient | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);

  // Detect platform
  useEffect(() => {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
    setPlatform(isMobile ? 'mobile' : 'desktop');
  }, []);

  // Initialize orbiting blobs with organic variation
  useEffect(() => {
    const blobCount = platform === 'mobile' ? 3 : 6;

    const colors = [
      tokens.color.enzyme,      // Cyan
      tokens.color.microtubule, // Teal
      tokens.color.endoplasmic, // Purple
    ];

    const newBlobs: OrbitingBlob[] = [];
    for (let i = 0; i < blobCount; i++) {
      const baseRadius = 20 + Math.random() * 20;
      newBlobs.push({
        id: i,
        angle: (Math.PI * 2 * i) / blobCount,
        baseDistance: 0.45 + Math.random() * 0.15, // 0.45-0.60 - closer for metaball merging
        distance: 0.45 + Math.random() * 0.15,
        baseRadius,
        radius: baseRadius,
        // VERY slow organic speed (0.0003-0.0007 = 5-10 seconds for full orbit)
        speed: 0.0003 + Math.random() * 0.0004,
        // Random phase offset for organic non-synchronized motion
        phaseOffset: Math.random() * Math.PI * 2,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    setBlobs(newBlobs);
  }, [platform]);

  // Audio analysis - get microphone level
  useEffect(() => {
    if (state !== 'listening' || !analyserRef.current) {
      setAudioLevel(0);
      return;
    }

    const analyser = analyserRef.current;
    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    const analyzeAudio = () => {
      if (state !== 'listening') {
        setAudioLevel(0);
        return;
      }

      analyser.getByteFrequencyData(dataArray);
      const sum = dataArray.reduce((a, b) => a + b, 0);
      const average = sum / dataArray.length;
      const normalizedLevel = Math.min(average / 80, 1);
      setAudioLevel(normalizedLevel);

      animationRef.current = requestAnimationFrame(analyzeAudio);
    };

    animationRef.current = requestAnimationFrame(analyzeAudio);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [state]);

  // Animate orbiting blobs with independent organic motion
  useEffect(() => {
    if (blobs.length === 0) return;

    let lastTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const deltaTime = (now - lastTime) / 1000; // Seconds
      lastTime = now;

      setBlobs((prev) =>
        prev.map((blob) => {
          // Update angle with independent speed
          let newAngle = blob.angle + blob.speed;

          // Organic distance variation - each blob breathes independently
          const time = now / 2000 + blob.phaseOffset; // 2-second cycle with offset
          const breathing = Math.sin(time) * 0.08; // +/- 8% distance variation
          let newDistance = blob.baseDistance + breathing;

          // Audio reactivity: loud sounds PUSH blobs OUT (audio force = outward pressure)
          if (state === 'listening') {
            const audioPush = audioLevel * 0.15; // Push up to 15% further on loud sounds
            newDistance = Math.min(0.85, newDistance + audioPush);

            // Pulse radius with audio - louder = bigger
            const audioScale = 1 + audioLevel * 0.5;
            const breathingScale = Math.sin(now / 600 + blob.phaseOffset) * 0.08 + 1;
            return {
              ...blob,
              angle: newAngle,
              distance: newDistance,
              radius: blob.baseRadius * breathingScale * audioScale,
              baseRadius: blob.baseRadius
            };
          }

          // Gentle breathing when idle
          const idleBreathing = Math.sin(now / 1500 + blob.phaseOffset) * 0.05 + 1;
          return {
            ...blob,
            angle: newAngle,
            distance: newDistance,
            radius: blob.baseRadius * idleBreathing,
            baseRadius: blob.baseRadius
          };
        })
      );

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [blobs.length, state, audioLevel]);

  // VoiceClient connection
  const connectVoiceClient = useCallback(() => {
    if (voiceClientRef.current) return;

    try {
      const client = new VoiceClient({
        url: `${BACKEND_WS_URL}/api/v1/voice/ws/voice`,
        maxReconnectAttempts: 0,
      });

      client.on(VoiceMessageType.CONFIG, () => {
        setIsConnected(true);
        console.log('[VoiceButton] Connected to voice server');
      });

      client.on(VoiceMessageType.AUDIO, (msg) => {
        if (typeof msg.data === 'string') playAudioResponse(msg.data);
      });

      client.on(VoiceMessageType.TEXT, (msg) => {
        console.log('[VoiceButton] Agent response:', msg.data);
        setState('idle');
      });

      client.on(VoiceMessageType.ERROR, (msg) => {
        console.error('[VoiceButton] Error:', msg.data);
        setIsConnected(false);
      });

      voiceClientRef.current = client;
      client.connect();
    } catch (error) {
      console.error('[VoiceButton] Failed to connect:', error);
      voiceClientRef.current = null;
      setIsConnected(false);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      voiceClientRef.current?.disconnect();
    };
  }, []);

  // Play audio response (base64 WAV)
  const playAudioResponse = useCallback(async (audioBase64: string) => {
    try {
      setState('speaking');
      const audioBytes = Uint8Array.from(atob(audioBase64), c => c.charCodeAt(0));
      const audioBlob = new Blob([audioBytes], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }
      const audioElement = new Audio(audioUrl);
      audioElement.onended = () => {
        setState('idle');
        URL.revokeObjectURL(audioUrl);
      };
      await audioElement.play();
    } catch (error) {
      console.error('[VoiceButton] Failed to play audio:', error);
      setState('idle');
    }
  }, []);

  // Start listening with audio analysis
  const startListening = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      if (!audioContextRef.current) {
        audioContextRef.current = new AudioContext();
      }

      const audioContext = audioContextRef.current;
      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const arrayBuffer = await audioBlob.arrayBuffer();
        const base64 = btoa(new Uint8Array(arrayBuffer).reduce((data, byte) => data + String.fromCharCode(byte), ''));
        voiceClientRef.current?.sendAudio(base64);
        setState('processing');
        stream.getTracks().forEach(track => track.stop());

        if (analyserRef.current) {
          analyserRef.current = null;
        }
      };

      mediaRecorderRef.current.start();
      setState('listening');
    } catch (error) {
      console.error('[VoiceButton] Failed to access microphone:', error);
    }
  }, []);

  // Stop listening
  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // Interrupt current operation
  const interrupt = useCallback(() => {
    stopListening();
    voiceClientRef.current?.sendInterrupt();
    setState('idle');
  }, [stopListening]);

  const handleClick = () => {
    if (!voiceClientRef.current) {
      connectVoiceClient();
      setIsConnected(true);
      return;
    }

    if (state === 'idle') {
      startListening();
    } else if (state === 'listening') {
      stopListening();
    } else if (state === 'processing' || state === 'speaking') {
      interrupt();
    }
  };

  const nucleusRadius = platform === 'mobile' ? tokens.spacing.voice : tokens.spacing.voiceDesktop;
  const blur = platform === 'mobile' ? tokens.metaball.mobileBlur : tokens.metaball.desktopBlur;

  // CRITICAL: Add padding to viewBox to prevent blur from being clipped
  const padding = blur * 2;
  const viewBoxSize = nucleusRadius + padding * 2;
  const centerOffset = padding + nucleusRadius / 2;

  const opacity = 1;
  const cursor = 'pointer';

  const getNucleusColor = (): string => {
    if (state === 'processing') return tokens.color.mitochondria; // Orange
    if (state === 'speaking') return tokens.color.microtubule; // Teal
    if (state === 'listening') return tokens.color.enzyme; // Cyan
    return tokens.color.mitochondria; // Orange (idle)
  };

  return (
    <button
      onClick={handleClick}
      className="relative flex items-center justify-center"
      style={{
        width: `${nucleusRadius}px`,
        height: `${nucleusRadius}px`,
        opacity,
        cursor,
        background: 'transparent',
        border: 'none',
        padding: 0,
      }}
      aria-label={state === 'idle' ? 'Start voice input' : `Voice: ${state}`}
    >
      {/* SVG Container with metaball effect and padded viewBox */}
      <svg
        className="absolute inset-0"
        style={{ width: '100%', height: '100%' }}
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
      >
        <defs>
          {/* SVG goo filter - CRITICAL for metaball effect */}
          <filter id={`goo-voice-${platform}`}>
            <feGaussianBlur in="SourceGraphic" stdDeviation={blur} result="blur" />
            <feColorMatrix
              in="blur"
              mode="matrix"
              values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -7"
              result="goo"
            />
          </filter>
        </defs>

        {/* Metaball group with goo filter */}
        <g filter={`url(#goo-voice-${platform})`}>
          {/* Orbiting blobs */}
          {blobs.map((blob) => {
            const orbitRadius = (nucleusRadius / 2) * blob.distance;
            const x = centerOffset + Math.cos(blob.angle) * orbitRadius;
            const y = centerOffset + Math.sin(blob.angle) * orbitRadius;

            return (
              <circle
                key={blob.id}
                cx={x}
                cy={y}
                r={blob.radius}
                fill={blob.color}
                opacity={0.85}
              />
            );
          })}

          {/* Central nucleus - PART OF METABALL SYSTEM */}
          <circle
            cx={centerOffset}
            cy={centerOffset}
            r={nucleusRadius / 3.2}
            fill={getNucleusColor()}
          />
        </g>

        {/* Inner icon (no goo filter - sharp display) */}
        <g
          style={{
            transformOrigin: `${centerOffset}px ${centerOffset}px`,
            animation: state === 'idle' && isConnected
              ? `drift ${motion.drift.duration}ms ease-in-out infinite`
              : undefined,
          }}
        >
          <style jsx>{`
            @keyframes drift {
              0%, 100% { transform: translateY(0px); }
              50% { transform: translateY(-8px); }
            }
          `}</style>

          {/* Mic icon */}
          <svg
            x={centerOffset - nucleusRadius * 0.15}
            y={centerOffset - nucleusRadius * 0.15}
            width={nucleusRadius * 0.3}
            height={nucleusRadius * 0.3}
            viewBox="0 0 24 24"
            fill={tokens.color.nucleus}
          >
            {state === 'idle' ? (
              <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.4C16.14 13.74 14.36 15 12 15c-2.36 0-4.14-1.26-4.93-2.6-.08-.04-.49-.4-.98-.4-.55 0-1 .45-1 1 0 2.28 1.45 4.28 3.91 5.35V18H10v-1.65C7.54 15.28 6.09 13.28 6.09 11c0-.55-.45-1-1-1z M12 20c-3.31 0-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8h-2c0 3.31-2.69 6-6 6z" />
            ) : state === 'listening' ? (
              <>
                <circle cx="12" cy="12" r="10" stroke={tokens.color.nucleus} strokeWidth="2" fill="none" opacity="0.3">
                  <animate attributeName="r" values="10;14;10" dur={`${motion.pulse.duration}ms`} repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.3;0.1;0.3" dur={`${motion.pulse.duration}ms`} repeatCount="indefinite" />
                </circle>
                <circle cx="12" cy="12" r="4" fill={tokens.color.nucleus} />
              </>
            ) : state === 'processing' ? (
              <circle cx="12" cy="12" r="10" stroke={tokens.color.nucleus} strokeWidth="2" fill="none">
                <animate attributeName="stroke-dasharray" values="0,63;63,63" dur="1s" repeatCount="indefinite" />
                <animate attributeName="stroke-dashoffset" values="63;-63" dur="1s" repeatCount="indefinite" />
              </circle>
            ) : (
              <>
                {[0, 1, 2].map((i) => (
                  <circle
                    key={i}
                    cx="12"
                    cy="12"
                    r={4 + i * 2}
                    stroke={tokens.color.nucleus}
                    strokeWidth="1"
                    fill="none"
                    opacity={1 - i * 0.3}
                  >
                    <animate attributeName="r" values={`${4 + i * 2};${8 + i * 2};${4 + i * 2}`} dur="1s" begin={`${i * 0.2}s`} repeatCount="indefinite" />
                    <animate attributeName="opacity" values={`${1 - i * 0.3};0;${1 - i * 0.3}`} dur="1s" begin={`${i * 0.2}s`} repeatCount="indefinite" />
                  </circle>
                ))}
              </>
            )}
          </svg>
        </g>
      </svg>

      {/* State indicator text */}
      <div
        className="absolute -bottom-8 text-sm font-medium"
        style={{ color: tokens.color.cytoplasm }}
      >
        {state === 'idle' && 'Tap to speak'}
        {state === 'listening' && 'Listening...'}
        {state === 'processing' && 'Processing...'}
        {state === 'speaking' && 'Speaking...'}
      </div>
    </button>
  );
}
