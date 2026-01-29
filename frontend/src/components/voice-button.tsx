/**
 * Organic UI voice nucleus button component (C008).
 *
 * Central voice interface component with platform-aware sizing.
 * Mobile: 72px radius
 * Desktop: 160px radius
 *
 * @see agentx_organic_ui_design_system.md
 */

'use client';

import { useState, useEffect } from 'react';
import { tokens } from '@/lib/design-tokens';

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

/**
 * Voice nucleus button component.
 *
 * Central circular button for voice interaction with organic design.
 * Platform-aware sizing and animations.
 */
export function VoiceButton() {
  const [state, setState] = useState<VoiceState>('idle');
  const [platform, setPlatform] = useState<'mobile' | 'desktop'>('desktop');

  // Detect platform
  useEffect(() => {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
    setPlatform(isMobile ? 'mobile' : 'desktop');
  }, []);

  const radius = platform === 'mobile'
    ? tokens.spacing.voice
    : tokens.spacing.voiceDesktop;

  const handleClick = () => {
    if (state === 'idle') {
      setState('listening');
      // Would start listening here
    } else if (state === 'listening') {
      setState('processing');
      // Would stop listening and process
    } else if (state === 'processing') {
      setState('speaking');
      // Would start speaking
    } else if (state === 'speaking') {
      setState('idle');
      // Would stop speaking
    }
  };

  const getButtonStyle = (): React.CSSProperties => {
    return {
      width: `${radius}px`,
      height: `${radius}px`,
      borderRadius: '50%',
      background: state === 'idle'
        ? 'rgba(0, 217, 255, 0.1)'
        : state === 'listening'
        ? 'rgba(0, 217, 255, 0.3)'
        : state === 'processing'
        ? 'rgba(255, 107, 53, 0.3)'
        : 'rgba(100, 255, 218, 0.3)',
      border: `2px solid ${tokens.color.enzyme}`,
      transition: 'all 0.3s ease',
    };
  };

  const getIconStyle = (): React.CSSProperties => {
    const size = radius * 0.4;
    return {
      width: `${size}px`,
      height: `${size}px`,
      fill: tokens.color.enzyme,
    };
  };

  return (
    <button
      onClick={handleClick}
      style={getButtonStyle()}
      className="flex items-center justify-center hover:scale-105 active:scale-95 transition-transform"
      aria-label={state === 'idle' ? 'Start voice input' : `Voice: ${state}`}
    >
      {/* Voice icon */}
      <svg style={getIconStyle()} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        {state === 'idle' ? (
          // Microphone icon
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.91-3c-.49 0-.9.36-.98.4C16.14 13.74 14.36 15 12 15c-2.36 0-4.14-1.26-4.93-2.6-.08-.04-.49-.4-.98-.4-.55 0-1 .45-1 1 0 2.28 1.45 4.28 3.91 5.35V18H10v-1.65C7.54 15.28 6.09 13.28 6.09 11c0-.55-.45-1-1-1z M12 20c-3.31 0-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8h-2c0 3.31-2.69 6-6 6z" />
        ) : state === 'listening' ? (
          // Listening animation
          <>
            <circle cx="12" cy="12" r="10" stroke={tokens.color.enzyme} strokeWidth="2" fill="none" opacity="0.3">
              <animate
                attributeName="r"
                values="10;14;10"
                dur="1s"
                repeatCount="indefinite"
              />
              <animate
                attributeName="opacity"
                values="0.3;0.1;0.3"
                dur="1s"
                repeatCount="indefinite"
              />
            </circle>
            <circle cx="12" cy="12" r="4" fill={tokens.color.enzyme} />
          </>
        ) : state === 'processing' ? (
          // Processing spinner
          <circle cx="12" cy="12" r="10" stroke={tokens.color.mitochondria} strokeWidth="2" fill="none">
            <animate
              attributeName="stroke-dasharray"
              values="0,63;63,63"
              dur="1s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="stroke-dashoffset"
              values="63;-63"
              dur="1s"
              repeatCount="indefinite"
            />
          </circle>
        ) : (
          // Speaking waves
          <>
            {[0, 1, 2].map((i) => (
              <circle
                key={i}
                cx="12"
                cy="12"
                r={4 + i * 2}
                stroke={tokens.color.microtubule}
                strokeWidth="1"
                fill="none"
                opacity={1 - i * 0.3}
              >
                <animate
                  attributeName="r"
                  values={`${4 + i * 2};${8 + i * 2};${4 + i * 2}`}
                  dur="1s"
                  begin={`${i * 0.2}s`}
                  repeatCount="indefinite"
                />
                <animate
                  attributeName="opacity"
                  values={`${1 - i * 0.3};0;${1 - i * 0.3}`}
                  dur="1s"
                  begin={`${i * 0.2}s`}
                  repeatCount="indefinite"
                />
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
        {state === 'idle' && 'Tap to speak'}
        {state === 'listening' && 'Listening...'}
        {state === 'processing' && 'Processing...'}
        {state === 'speaking' && 'Speaking...'}
      </div>
    </button>
  );
}
