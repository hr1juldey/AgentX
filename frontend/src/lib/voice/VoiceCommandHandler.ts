/**
 * Voice Command Handler for predictable STT command recognition.
 *
 * Trigger word: "hello Shiba" (normalized from shiva/shiba/siba variants)
 * Commands:
 *   - "echo off" - Disable echo mode
 *   - "echo on" - Enable echo mode
 *   - "agent on" - Enable AgentX voice mode
 *   - "agent off" - Disable AgentX voice mode
 *
 * Echo and Agent modes are mutually exclusive.
 */

export type VoiceMode = 'echo' | 'agent' | 'none';
export type CommandResult =
  | { type: 'trigger_activated' }
  | { type: 'echo_on' }
  | { type: 'echo_off' }
  | { type: 'agent_on' }
  | { type: 'agent_off' }
  | { type: 'unknown' }
  | { type: 'no_trigger' };

export interface VoiceCommandState {
  mode: VoiceMode;
  commandActive: boolean;
  lastCommand: string;
}

// Trigger word variants (all normalized to "hello shiba")
const TRIGGER_VARIANTS = ['hello shiva', 'hello siba'];
const NORMALIZED_TRIGGER = 'hello shiba';

const COMMANDS = {
  ECHO_ON: 'echo on',
  ECHO_OFF: 'echo off',
  AGENT_ON: 'agent on',
  AGENT_OFF: 'agent off',
} as const;

/**
 * Normalize text for command matching.
 * - Convert to lowercase
 * - Remove punctuation (periods, commas, etc.)
 * - Normalize trigger word variants (shiva/shiba/siba → shiba)
 * - Remove extra whitespace
 * - Trim leading/trailing spaces
 */
function normalizeText(text: string): string {
  // Remove common punctuation first
  let normalized = text
    .toLowerCase()
    .replace(/[.,!?;:'""]/g, '')  // Remove punctuation
    .trim()
    .replace(/\s+/g, ' ');

  // Normalize trigger word variants
  TRIGGER_VARIANTS.forEach((variant) => {
    normalized = normalized.replace(variant, NORMALIZED_TRIGGER);
  });

  return normalized;
}

/**
 * Check if text contains the trigger word.
 */
function hasTriggerWord(text: string): boolean {
  const normalized = normalizeText(text);
  return normalized.includes(NORMALIZED_TRIGGER);
}

/**
 * Extract command from text (must be exact match after trigger word).
 */
function extractCommand(text: string): string | null {
  const normalized = normalizeText(text);

  // Remove trigger word
  const afterTrigger = normalized.replace(NORMALIZED_TRIGGER, '').trim();

  // Debug logging
  console.log('[VoiceCommandHandler] extractCommand:', {
    input: text,
    normalized,
    afterTrigger,
    expected_on: COMMANDS.ECHO_ON,
    expected_off: COMMANDS.ECHO_OFF,
  });

  // Check for exact command matches (must be ONLY the command)
  if (afterTrigger === COMMANDS.ECHO_ON) return COMMANDS.ECHO_ON;
  if (afterTrigger === COMMANDS.ECHO_OFF) return COMMANDS.ECHO_OFF;
  if (afterTrigger === COMMANDS.AGENT_ON) return COMMANDS.AGENT_ON;
  if (afterTrigger === COMMANDS.AGENT_OFF) return COMMANDS.AGENT_OFF;

  // Check if it's just the trigger word alone
  if (afterTrigger === '' || afterTrigger === NORMALIZED_TRIGGER) {
    return 'trigger_only';
  }

  return null;
}

export class VoiceCommandHandler {
  private state: VoiceCommandState = {
    mode: 'none',
    commandActive: false,
    lastCommand: '',
  };
  private listeners: Set<(state: VoiceCommandState) => void> = new Set();

  /**
   * Subscribe to state changes.
   */
  subscribe(listener: (state: VoiceCommandState) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Get current state.
   */
  getState(): VoiceCommandState {
    return { ...this.state };
  }

  /**
   * Get current mode.
   */
  getMode(): VoiceMode {
    return this.state.mode;
  }

  /**
   * Check if agent mode is active.
   */
  isAgentMode(): boolean {
    return this.state.mode === 'agent';
  }

  /**
   * Check if echo mode is active.
   */
  isEchoMode(): boolean {
    return this.state.mode === 'echo';
  }

  /**
   * Process transcription and return command result.
   */
  processTranscription(transcription: string): CommandResult {
    const normalized = normalizeText(transcription);

    // Check for trigger word
    if (!hasTriggerWord(normalized)) {
      return { type: 'no_trigger' };
    }

    // Extract command
    const command = extractCommand(normalized);

    // Activate command mode on trigger word detection
    this.state.commandActive = true;

    // Handle command
    switch (command) {
      case COMMANDS.ECHO_ON:
        this.state.mode = 'echo';
        this.state.lastCommand = COMMANDS.ECHO_ON;
        this.notifyListeners();
        return { type: 'echo_on' };

      case COMMANDS.ECHO_OFF:
        this.state.mode = 'none';
        this.state.lastCommand = COMMANDS.ECHO_OFF;
        this.notifyListeners();
        return { type: 'echo_off' };

      case COMMANDS.AGENT_ON:
        this.state.mode = 'agent';
        this.state.lastCommand = COMMANDS.AGENT_ON;
        this.notifyListeners();
        return { type: 'agent_on' };

      case COMMANDS.AGENT_OFF:
        this.state.mode = 'none';
        this.state.lastCommand = COMMANDS.AGENT_OFF;
        this.notifyListeners();
        return { type: 'agent_off' };

      case 'trigger_only':
        this.state.lastCommand = NORMALIZED_TRIGGER;
        this.notifyListeners();
        return { type: 'trigger_activated' };

      default:
        // Unknown text after trigger word
        this.state.lastCommand = normalized;
        this.notifyListeners();
        return { type: 'unknown' };
    }
  }

  /**
   * Reset command mode (e.g., after timeout).
   */
  resetCommandMode(): void {
    this.state.commandActive = false;
    this.notifyListeners();
  }

  /**
   * Reset to initial state.
   */
  reset(): void {
    this.state = {
      mode: 'none',
      commandActive: false,
      lastCommand: '',
    };
    this.notifyListeners();
  }

  /**
   * Notify all listeners of state change.
   */
  private notifyListeners(): void {
    this.listeners.forEach((listener) => listener({ ...this.state }));
  }
}

/**
 * Global singleton instance.
 */
let globalHandler: VoiceCommandHandler | null = null;

export function getVoiceCommandHandler(): VoiceCommandHandler {
  if (!globalHandler) {
    globalHandler = new VoiceCommandHandler();
  }
  return globalHandler;
}

/**
 * Reset command mode after inactivity timeout.
 */
export function startCommandModeTimeout(
  handler: VoiceCommandHandler,
  timeoutMs: number = 10000
): () => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;

  const resetTimeout = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    timeoutId = setTimeout(() => {
      handler.resetCommandMode();
    }, timeoutMs);
  };

  resetTimeout();

  // Return cleanup function
  return () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
  };
}
