/**
 * Organic UI voice nucleus button component (C008) - Direct Kyutai Echo Loop.
 *
 * This version bypasses the AgentX backend and connects directly to Kyutai
 * for STT → Echo text → TTS to verify the full pipeline works.
 *
 * Connections are opened on-demand to avoid Kyutai's 60-second timeout.
 *
 * @see agentx_organic_ui_design_system.md
 */

'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { tokens, motion } from '@/lib/design-tokens';
import { AudioProcessor } from '@/lib/audio/AudioProcessor';

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

const KYUTAI_STT_URL = 'ws://localhost:16000/api/v1/ws/stt';
const KYUTAI_TTS_URL = 'ws://localhost:16000/api/v1/ws/tts';

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
 * Voice nucleus button with direct Kyutai echo loop.
 */
export function VoiceButton() {
  const [state, setState] = useState<VoiceState>('idle');
  const [platform, setPlatform] = useState<'mobile' | 'desktop'>('desktop');
  const [blobs, setBlobs] = useState<OrbitingBlob[]>([]);
  const [audioLevel, setAudioLevel] = useState(0);

  const audioProcessorRef = useRef<AudioProcessor | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);

  const sttWebSocketRef = useRef<WebSocket | null>(null);
  const ttsWebSocketRef = useRef<WebSocket | null>(null);
  const transcriptionRef = useRef<string | null>(null);
  const sessionIdRef = useRef<string | null>(null);

  // Detect platform
  useEffect(() => {
    const isMobile = /Mobile|Android|iPhone/i.test(navigator.userAgent);
    setPlatform(isMobile ? 'mobile' : 'desktop');
  }, []);

  // Initialize orbiting blobs
  useEffect(() => {
    const blobCount = platform === 'mobile' ? 3 : 6;
    const colors = [
      tokens.color.enzyme,
      tokens.color.microtubule,
      tokens.color.endoplasmic,
    ];

    const newBlobs: OrbitingBlob[] = [];
    for (let i = 0; i < blobCount; i++) {
      const baseRadius = 20 + Math.random() * 20;
      newBlobs.push({
        id: i,
        angle: (Math.PI * 2 * i) / blobCount,
        baseDistance: 0.45 + Math.random() * 0.15,
        distance: 0.45 + Math.random() * 0.15,
        baseRadius,
        radius: baseRadius,
        speed: 0.0003 + Math.random() * 0.0004,
        phaseOffset: Math.random() * Math.PI * 2,
        color: colors[Math.floor(Math.random() * colors.length)],
      });
    }

    setBlobs(newBlobs);
  }, [platform]);

  // Audio analysis
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

  // Animate blobs
  useEffect(() => {
    if (blobs.length === 0) return;

    let lastTime = Date.now();

    const animate = () => {
      const now = Date.now();
      const deltaTime = (now - lastTime) / 1000;
      lastTime = now;

      setBlobs((prev) =>
        prev.map((blob) => {
          let newAngle = blob.angle + blob.speed;
          const time = now / 2000 + blob.phaseOffset;
          const breathing = Math.sin(time) * 0.08;
          let newDistance = blob.baseDistance + breathing;

          if (state === 'listening') {
            const audioPush = audioLevel * 0.15;
            newDistance = Math.min(0.85, newDistance + audioPush);
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

  // Connect to STT (on-demand, when recording starts)
  const connectSTT = useCallback((sessionId: string): Promise<WebSocket> => {
    return new Promise((resolve, reject) => {
      const sttWs = new WebSocket(`${KYUTAI_STT_URL}?encoding=json`);
      sttWs.binaryType = 'blob';

      sttWs.onopen = () => {
        console.log('[Kyutai Direct] STT connected');
        // Send config message with session_id
        sttWs.send(JSON.stringify({
          type: 'Config',
          data: {
            streaming_mode: 'both',
            input_format: 'int16',
          },
          session_id: sessionId,
        }));
        resolve(sttWs);
      };

      sttWs.onerror = (error) => {
        console.error('[Kyutai Direct] STT error:', error);
        reject(error);
      };

      sttWebSocketRef.current = sttWs;
    });
  }, []);

  // Connect to TTS (on-demand, after transcription received)
  const connectTTS = useCallback((sessionId: string): Promise<WebSocket> => {
    return new Promise((resolve, reject) => {
      const ttsWs = new WebSocket(`${KYUTAI_TTS_URL}?encoding=json`);
      ttsWs.binaryType = 'blob';

      ttsWs.onopen = () => {
        console.log('[Kyutai Direct] TTS connected');
        // Send config message with session_id
        ttsWs.send(JSON.stringify({
          type: 'Config',
          data: {},
          session_id: sessionId,
        }));
        resolve(ttsWs);
      };

      ttsWs.onerror = (error) => {
        console.error('[Kyutai Direct] TTS error:', error);
        reject(error);
      };

      ttsWebSocketRef.current = ttsWs;
    });
  }, []);

  // Start listening
  const startListening = useCallback(async () => {
    try {
      // Generate session ID for this voice loop (shared by STT and TTS)
      const sessionId = crypto.randomUUID();
      sessionIdRef.current = sessionId;

      // Get microphone access for visualization
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

      // Connect to STT now
      const sttWs = await connectSTT(sessionId);

      // Create audio processor for 16kHz PCM streaming
      const processor = new AudioProcessor(
        {
          targetSampleRate: 16000, // Whisper requirement
          channels: 1, // Mono
          chunkDurationMs: 200, // 200ms chunks
        },
        {
          onChunk: (pcmBase64: string) => {
            // Stream chunk to STT
            if (sttWebSocketRef.current?.readyState === WebSocket.OPEN) {
              sttWebSocketRef.current.send(JSON.stringify({
                type: 'Audio',
                data: pcmBase64,
                session_id: sessionIdRef.current,
              }));
            }
          },
          onError: (error: Error) => {
            console.error('[Kyutai Direct] Audio processor error:', error);
            setState('idle');
          },
        }
      );

      audioProcessorRef.current = processor;

      // Set up STT message handler
      sttWs.onmessage = async (event) => {
        const msg = JSON.parse(event.data);
        console.log('[Kyutai Direct] STT message:', msg);

        if (msg.type === 'Text' && msg.is_final) {
          // Got final transcription
          const transcription = msg.data;
          transcriptionRef.current = transcription;
          console.log('[Kyutai Direct] Transcription:', transcription);

          // Close STT connection
          sttWs.close();
          sttWebSocketRef.current = null;

          // Now connect to TTS and send text
          setState('processing');
          const ttsWs = await connectTTS(sessionId);

          // Accumulate audio chunks
          const audioChunks: Uint8Array[] = [];
          let sampleRate = 24000;
          let numChannels = 1;

          ttsWs.onmessage = async (event) => {
            const ttsMsg = JSON.parse(event.data);
            console.log('[Kyutai Direct] TTS message type:', ttsMsg.type, 'full:', ttsMsg);

            if (ttsMsg.type === 'Audio') {
              setState('speaking');
              // Kyutai TTS sends audio data directly in 'data' field as base64 string
              // The message structure is: { type: "Audio", data: "base64...", format: "pcm_int16", sample_rate: 24000, channels: 1 }
              const audioData = ttsMsg.data;
              if (audioData && typeof audioData === 'string') {
                const audioBase64 = audioData.replace(/\s/g, '');
                const audioBytes = Uint8Array.from(atob(audioBase64), c => c.charCodeAt(0));
                audioChunks.push(audioBytes);
                sampleRate = ttsMsg.sample_rate || 24000;
                numChannels = ttsMsg.channels || 1;
                console.log('[Kyutai Direct] Accumulated audio chunk:', audioChunks.length, 'total bytes:', audioChunks.reduce((sum, c) => sum + c.length, 0));
              } else {
                console.warn('[Kyutai Direct] Audio message missing audio data:', ttsMsg);
              }
            } else if (ttsMsg.type === 'Eos') {
              console.log('[Kyutai Direct] TTS EOS received, combining', audioChunks.length, 'chunks');
              // All chunks received - combine and play
              if (audioChunks.length > 0) {
                const totalPcmSize = audioChunks.reduce((sum, chunk) => sum + chunk.length, 0);
                const combinedPcm = new Uint8Array(totalPcmSize);
                let offset = 0;
                for (const chunk of audioChunks) {
                  combinedPcm.set(chunk, offset);
                  offset += chunk.length;
                }

                // Create WAV header for combined PCM
                const bitsPerSample = 16;
                const byteRate = sampleRate * numChannels * bitsPerSample / 8;
                const blockAlign = numChannels * bitsPerSample / 8;
                const dataSize = combinedPcm.length;
                const headerSize = 44;
                const totalSize = headerSize + dataSize;

                const wavBuffer = new ArrayBuffer(totalSize);
                const view = new DataView(wavBuffer);

                // Write WAV header
                const writeString = (offset: number, string: string) => {
                  for (let i = 0; i < string.length; i++) {
                    view.setUint8(offset + i, string.charCodeAt(i));
                  }
                };

                // RIFF chunk descriptor
                writeString(0, 'RIFF');
                view.setUint32(4, totalSize - 8, true);
                writeString(8, 'WAVE');

                // fmt sub-chunk
                writeString(12, 'fmt ');
                view.setUint32(16, 16, true);
                view.setUint16(20, 1, true);
                view.setUint16(22, numChannels, true);
                view.setUint32(24, sampleRate, true);
                view.setUint32(28, byteRate, true);
                view.setUint16(32, blockAlign, true);
                view.setUint16(34, bitsPerSample, true);

                // data sub-chunk
                writeString(36, 'data');
                view.setUint32(40, dataSize, true);

                // Copy combined PCM data
                new Uint8Array(wavBuffer, headerSize).set(combinedPcm);

                // Create and play audio
                const audioBlob = new Blob([wavBuffer], { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(audioBlob);

                const audio = new Audio(audioUrl);
                audio.onended = () => {
                  console.log('[Kyutai Direct] Audio playback finished');
                  URL.revokeObjectURL(audioUrl);
                  // Close TTS connection after audio finishes
                  ttsWs.close();
                  ttsWebSocketRef.current = null;
                  setState('idle');
                };
                audio.onerror = (error) => {
                  console.error('[Kyutai Direct] Audio playback error:', error);
                  URL.revokeObjectURL(audioUrl);
                  ttsWs.close();
                  ttsWebSocketRef.current = null;
                  setState('idle');
                };
                console.log('[Kyutai Direct] Playing audio, size:', totalPcmSize, 'bytes');
                await audio.play();
              } else {
                console.warn('[Kyutai Direct] No audio chunks received');
                // No audio chunks - close connection
                ttsWs.close();
                ttsWebSocketRef.current = null;
                setState('idle');
              }
            } else {
              console.warn('[Kyutai Direct] Unhandled TTS message type:', ttsMsg.type, 'message:', ttsMsg);
            }
          };

          // Send text to TTS with session_id
          ttsWs.send(JSON.stringify({
            type: 'Text',
            data: transcription,
            session_id: sessionIdRef.current,
          }));
        } else if (msg.type === 'Eos') {
          // STT finished - check if we got a transcription
          // Wait a moment in case Text message arrives after Eos
          setTimeout(() => {
            if (!transcriptionRef.current && sttWebSocketRef.current) {
              console.warn('[Kyutai Direct] No transcription received from STT (may have filtered out all audio)');
              sttWs.close();
              sttWebSocketRef.current = null;
              setState('idle');
            }
          }, 500); // Wait 500ms for potential late Text message
        }
      };

      // Start recording
      await processor.start();
      setState('listening');
      console.log('[Kyutai Direct] Started listening with 16kHz PCM streaming');
    } catch (error) {
      console.error('[Kyutai Direct] Failed to access microphone:', error);
      setState('idle');
    }
  }, [connectSTT, connectTTS]);

  // Stop listening
  const stopListening = useCallback(() => {
    if (audioProcessorRef.current && audioProcessorRef.current.recording) {
      audioProcessorRef.current.stop();

      // Send EOS to STT
      if (sttWebSocketRef.current?.readyState === WebSocket.OPEN) {
        sttWebSocketRef.current.send(JSON.stringify({
          type: 'Eos',
          data: null,
          session_id: sessionIdRef.current,
        }));
      }

      setState('processing');
      console.log('[Kyutai Direct] Stopped listening, sent EOS');

      // Cleanup analyser
      if (analyserRef.current) {
        analyserRef.current = null;
      }
    }
  }, []);

  // Interrupt
  const interrupt = useCallback(() => {
    // Stop audio processor if recording
    if (audioProcessorRef.current && audioProcessorRef.current.recording) {
      audioProcessorRef.current.stop();
    }

    // Close any open connections
    sttWebSocketRef.current?.close();
    ttsWebSocketRef.current?.close();
    sttWebSocketRef.current = null;
    ttsWebSocketRef.current = null;
    setState('idle');
  }, []);

  // Handle click
  const handleClick = () => {
    if (state === 'idle') {
      startListening();
    } else if (state === 'listening') {
      stopListening();
    } else if (state === 'processing' || state === 'speaking') {
      interrupt();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log('[Kyutai Direct] Component unmounting, closing connections...');
      sttWebSocketRef.current?.close();
      ttsWebSocketRef.current?.close();
    };
  }, []);

  // Debug: Log state changes to detect re-renders
  useEffect(() => {
    console.log('[Kyutai Direct] State changed to:', state);
  }, [state]);

  const nucleusRadius = platform === 'mobile' ? tokens.spacing.voice : tokens.spacing.voiceDesktop;
  const blur = platform === 'mobile' ? tokens.metaball.mobileBlur : tokens.metaball.desktopBlur;
  const padding = blur * 2;
  const viewBoxSize = nucleusRadius + padding * 2;
  const centerOffset = padding + nucleusRadius / 2;

  const getNucleusColor = (): string => {
    if (state === 'processing') return tokens.color.mitochondria;
    if (state === 'speaking') return tokens.color.microtubule;
    if (state === 'listening') return tokens.color.enzyme;
    return tokens.color.mitochondria;
  };

  return (
    <button
      onClick={handleClick}
      className="relative flex items-center justify-center"
      style={{
        width: `${nucleusRadius}px`,
        height: `${nucleusRadius}px`,
        opacity: 1,
        cursor: 'pointer',
        background: 'transparent',
        border: 'none',
        padding: 0,
      }}
      aria-label={state === 'idle' ? 'Start voice input' : `Voice: ${state}`}
    >
      <svg
        className="absolute inset-0"
        style={{ width: '100%', height: '100%' }}
        xmlns="http://www.w3.org/2000/svg"
        viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
      >
        <defs>
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

        <g filter={`url(#goo-voice-${platform})`}>
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

          <circle
            cx={centerOffset}
            cy={centerOffset}
            r={nucleusRadius / 3.2}
            fill={getNucleusColor()}
          />
        </g>

        <g
          style={{
            transformOrigin: `${centerOffset}px ${centerOffset}px`,
            animation: state === 'idle' ? `drift ${motion.drift.duration}ms ease-in-out infinite` : undefined,
          }}
        >
          <style jsx>{`
            @keyframes drift {
              0%, 100% { transform: translateY(0px); }
              50% { transform: translateY(-8px); }
            }
          `}</style>

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
                <circle cx="12" cy="12" r="10" stroke={tokens.color.nucleus} strokeWidth="2" fill="none" opacity={0.3}>
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
