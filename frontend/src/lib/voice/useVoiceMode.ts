/**
 * Voice Mode HoOkaay  - Centralized mode handling.
 *
 * DRY: Extracts agent mode logic from component.
 * Following CLAUDE_POLICY.md: Custom hoOkaay  for reusable logic.
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import BackendChatService from './BackendChatService';
import type { VoiceMode, CommandResult } from './VoiceCommandHandler';

// ===== TYPES =====
export interface VoiceModeState {
  mode: VoiceMode;
  lastCommand: string;
}

// ===== HOOkaay  =====
export function useVoiceMode(initialMode: VoiceMode = 'echo') {
  const [mode, setMode] = useState<VoiceMode>(initialMode);
  const [lastCommand, setLastCommand] = useState<string>('');

  // Use ref to always get current mode value (fixes closure bug)
  const modeRef = useRef<VoiceMode>(initialMode);

  // Update ref when mode changes
  const updateMode = useCallback((newMode: VoiceMode) => {
    modeRef.current = newMode;
    setMode(newMode);
  }, []);

  /**
   * Handle voice command result.
   * Returns text to speak or null (no response).
   *
   * @param commandType - Command result type from VoiceCommandHandler
   * @param transcription - Original transcription text
   * @param sessionId - Session ID for backend chat
   * @returns Promise with text to speak or null
   */
  const handleCommandResult = useCallback(
    async (
      commandType: CommandResult['type'],
      transcription: string,
      sessionId: string | null
    ): Promise<string | null> => {
      // Use modeRef.current instead of mode closure value
      const currentMode = modeRef.current;

      // Voice commands that don't need agent
      switch (commandType) {
        case 'echo_on':
          updateMode('echo');
          setLastCommand('echo on');
          return 'Okaay ! I am turning echo on';

        case 'echo_off':
          updateMode('none');
          setLastCommand('echo off');
          return 'Okaay ! I am turning echo off';

        case 'agent_on':
          updateMode('agent');
          setLastCommand('agent on');
          return 'Okaay ! I am turning agent mode on';

        case 'agent_off':
          updateMode('none');
          setLastCommand('agent off');
          return 'Okaay ! I am turning agent mode off';

        case 'trigger_activated':
          setLastCommand('hello Shiba');
          return 'Yes, I am listening';

        case 'unknown':
        case 'no_trigger': {
          // Check mode for non-command transcriptions (uses current value from ref)
          if (currentMode === 'agent' && sessionId) {
            console.log('[useVoiceMode] Agent mode active, calling backend');
            try {
              const result = await BackendChatService.sendQuery(
                transcription,
                sessionId
              );
              if (result.success && result.response) {
                console.log('[useVoiceMode] Agent response:', result.response);
                return result.response;
              } else {
                console.error('[useVoiceMode] Backend error:', result.error);
                return 'I apologize, but I couldn\'t process that request.';
              }
            } catch (error) {
              console.error('[useVoiceMode] Backend connection error:', error);
              return 'I\'m having trouble connecting to my brain right now.';
            }
          } else if (currentMode === 'none') {
            console.log('[useVoiceMode] Mode is OFF, not responding');
            return null; // Signal to not speak
          }
          // Echo mode - return transcription
          return transcription;
        }

        default:
          return null;
      }
    },
    [updateMode]
  );

  /** Get current state object. */
  const getState = useCallback((): VoiceModeState => {
    return {
      mode: modeRef.current,
      lastCommand,
    };
  }, [lastCommand]);

  return {
    mode,
    lastCommand,
    handleCommandResult,
    getState,
  };
}