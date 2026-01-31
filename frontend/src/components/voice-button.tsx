/**
 * Organic UI voice nucleus button component (C008).
 *
 * Central voice interface component with platform-aware sizing.
 * Mobile: 72px radius
 * Desktop: 160px radius
 *
 * Integrated with VoiceClient for WebSocket voice communication.
 *
 * Uses motion presets: pulse (active), drift (idle).
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

/**
 * Voice nucleus button component with full WebSocket integration.
 *
 * Central circular button for voice interaction with organic design.
 * Platform-aware sizing and animations using motion presets.
 */
export function VoiceButton() {
  const [state, setState] = useState<VoiceState>('idle');
  const [platform, setPlatform] = useState<'mobile' | 'desktop'>('desktop');
  const [isConnected, setIsConnected] = useState(false);

  const voiceClientRef = useRef<VoiceClient | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);

  // Initialize VoiceClient
  useEffect(() => {
    const client = new VoiceClient({
      url: `${BACKEND_WS_URL}/api/v1/voice/ws/voice`,
    });

    client.on(VoiceMessageType.CONFIG, () => setIsConnected(true));
    client.on(VoiceMessageType.AUDIO, (msg) => {
      if (typeof msg.data === 'string') playAudioResponse(msg.data);
    });
    client.on(VoiceMessageType.TEXT, (msg) => {
      console.log('[VoiceButton] Agent response:', msg.data);
      setState('idle');
    });
    client.on(VoiceMessageType.ERROR, (msg) => {
      console.error('[VoiceButton] Error:', msg.data);
      setState('idle');
    });

    voiceClientRef.current = client;
    client.connect();

    return () => client.disconnect();
  }, []);

  // Detect platform
  useEffect(() => {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
    setPlatform(isMobile ? 'mobile' : 'desktop');
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

  // Start listening
  const startListening = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
    if (state === 'idle' && isConnected) {
      startListening();
    } else if (state === 'listening') {
      stopListening();
    } else if (state === 'processing' || state === 'speaking') {
      interrupt();
    }
  };

  const radius = platform === 'mobile' ? tokens.spacing.voice : tokens.spacing.voiceDesktop;

  // Connection-aware styling
  const borderColor = isConnected ? tokens.color.enzyme : tokens.color.vacuole;
  const opacity = isConnected ? 1 : 0.5;
  const cursor = isConnected ? 'pointer' : 'not-allowed';

  // State-based background colors using tokens
  const getBackground = (): string => {
    const enzymeAlpha = state === 'idle' ? '0.1' : state === 'listening' ? '0.3' : '0.2';
    if (state === 'processing') return `rgba(255, 107, 53, 0.3)`;
    if (state === 'speaking') return `rgba(100, 255, 218, 0.3)`;
    return `rgba(0, 217, 255, ${enzymeAlpha})`;
  };

  return (
    <button
      onClick={handleClick}
      className="relative flex items-center justify-center"
      style={{
        width: `${radius}px`,
        height: `${radius}px`,
        borderRadius: '50%',
        background: getBackground(),
        border: `2px solid ${borderColor}`,
        transition: `all ${tokens.motion.duration.normal}ms ${tokens.motion.easing.default}`,
        opacity,
        cursor,
        animation: state !== 'idle' && isConnected
          ? `pulse ${motion.pulse.duration}ms ease-in-out infinite`
          : undefined,
      }}
      aria-label={state === 'idle' ? 'Start voice input' : `Voice: ${state}`}
    >
      {/* Drift animation when idle */}
      {state === 'idle' && isConnected && (
        <style jsx>{`
          @keyframes drift {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
          }
        `}</style>
      )}

      {/* SVG Icon */}
      <svg
        style={{
          width: `${radius * 0.4}px`,
          height: `${radius * 0.4}px`,
          animation: state === 'idle' && isConnected
            ? `drift ${motion.drift.duration}ms ease-in-out infinite`
            : undefined,
        }}
        viewBox="0 0 24 24"
      >
        {state === 'idle' ? (
          <path fill={tokens.color.enzyme} d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.4C16.14 13.74 14.36 15 12 15c-2.36 0-4.14-1.26-4.93-2.6-.08-.04-.49-.4-.98-.4-.55 0-1 .45-1 1 0 2.28 1.45 4.28 3.91 5.35V18H10v-1.65C7.54 15.28 6.09 13.28 6.09 11c0-.55-.45-1-1-1z M12 20c-3.31 0-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8h-2c0 3.31-2.69 6-6 6z" />
        ) : state === 'listening' ? (
          <>
            <circle cx="12" cy="12" r="10" stroke={tokens.color.enzyme} strokeWidth="2" fill="none" opacity="0.3">
              <animate attributeName="r" values="10;14;10" dur={`${motion.pulse.duration}ms`} repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.3;0.1;0.3" dur={`${motion.pulse.duration}ms`} repeatCount="indefinite" />
            </circle>
            <circle cx="12" cy="12" r="4" fill={tokens.color.enzyme} />
          </>
        ) : state === 'processing' ? (
          <circle cx="12" cy="12" r="10" stroke={tokens.color.mitochondria} strokeWidth="2" fill="none">
            <animate attributeName="stroke-dasharray" values="0,63;63,63" dur="1s" repeatCount="indefinite" />
            <animate attributeName="stroke-dashoffset" values="63;-63" dur="1s" repeatCount="indefinite" />
          </circle>
        ) : (
          <>
            {[0, 1, 2].map((i) => (
              <circle
                key={i}
                cx="12" cy="12" r={4 + i * 2}
                stroke={tokens.color.microtubule} strokeWidth="1" fill="none"
                opacity={1 - i * 0.3}
              >
                <animate attributeName="r" values={`${4 + i * 2};${8 + i * 2};${4 + i * 2}`} dur="1s" begin={`${i * 0.2}s`} repeatCount="indefinite" />
                <animate attributeName="opacity" values={`${1 - i * 0.3};0;${1 - i * 0.3}`} dur="1s" begin={`${i * 0.2}s`} repeatCount="indefinite" />
              </circle>
            ))}
          </>
        )}
      </svg>

      {/* State indicator text */}
      <div
        className="absolute -bottom-8 text-sm font-medium"
        style={{ color: tokens.color.cytoplasm }}
      >
        {!isConnected && 'Connecting...'}
        {state === 'idle' && isConnected && 'Tap to speak'}
        {state === 'listening' && 'Listening...'}
        {state === 'processing' && 'Processing...'}
        {state === 'speaking' && 'Speaking...'}
      </div>
    </button>
  );
}
