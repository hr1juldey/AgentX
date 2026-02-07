/**
 * Main page for Real AgentX v0.1.
 *
 * Implements LangGraph server-driven UI (C007) with Organic UI visual layer (C008).
 *
 * @see agentx_organic_ui_design_system.md
 * @see c007-frontend-architecture
 */

'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { useStream } from '@/hooks/useLangGraph';
import { LoadExternalComponent } from '@/components/ui/LoadExternalComponent';

import { tokens } from '@/lib/design-tokens';
import { MetaballBackground } from '@/components/metaball-canvas';
import { VoiceButton } from '@/components/voice-button-kyutai-direct';
import { useWebSocket } from '@/hooks/useWebSocket';

// Backend API configuration - supports both localhost and network IP
const BACKEND_URL = 'http://localhost:8015/api/v1';
const BACKEND_WS_URL = 'ws://localhost:8015/api/v1/ws/chat';  // Chat endpoint for text
// Alternative: Use network IP for mobile access
// const BACKEND_URL = 'http://192.168.1.4:8015/api/v1';
// const BACKEND_WS_URL = 'ws://192.168.1.4:8015/api/v1/ws/chat';

/**
 * Main page component.
 *
 * Features:
 * - LangGraph server-driven UI with useStream hook
 * - Organic UI metaball background (C008)
 * - Voice nucleus button (C008)
 * - WebSocket real-time communication
 */
export default function HomePage() {
  const [query, setQuery] = useState('');
  const [threadId, setThreadId] = useState<string | null>(null);

  // WebSocket connection for real-time chat updates
  const { isConnected, sendMessage } = useWebSocket(BACKEND_WS_URL);

  // LangGraph stream integration (C007)
  const { thread, values } = useStream({
    apiUrl: BACKEND_URL,
    threadId: threadId || undefined,
    onCustomEvent: useCallback((event: any, options: any) => {
      // Handle UI component events from server-driven UI
      options?.mutate?.((prev: any) => {
        const ui = prev.ui ?? [];
        const newUi = [...ui];

        // Merge or add component
        if (event.merge) {
          const index = newUi.findIndex((u: any) => u.id === event.id);
          if (index >= 0) {
            newUi[index] = { ...newUi[index], ...event };
          }
        } else {
          newUi.push(event);
        }

        return { ...prev, ui: newUi };
      });
    }, []),
  });

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    // Send query via WebSocket
    sendMessage({
      message_type: 'query',
      data: { query },
      session_id: threadId ?? null,
    });

    // Note: LangGraph stream handles queries via the WebSocket endpoint
    // The useStream hook listens for updates automatically

    setQuery('');
  }, [query, threadId, sendMessage]);

  return (
    <main className="min-h-screen bg-void text-nucleus relative overflow-hidden">
      {/* Organic UI metaball background (C008) */}
      <MetaballBackground />

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 border-b border-membrane/50 backdrop-blur-sm">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-nucleus flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-enzyme animate-pulse" />
                AgentX
              </h1>
              <p className="text-sm text-cytoplasm mt-1">
                Organic AI Assistant
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Link
                href="/library"
                className="px-3 py-1.5 rounded-lg text-sm font-medium transition-all hover:opacity-80"
                style={{
                  backgroundColor: 'rgba(0, 217, 255, 0.1)',
                  color: tokens.color.enzyme,
                }}
              >
                Design Library
              </Link>
              <div
                className={`w-2 h-2 rounded-full transition-colors ${
                  isConnected ? 'bg-enzyme' : 'bg-vacuole'
                }`}
              />
              <span className="text-xs text-cytoplasm">
                {isConnected ? 'Connected' : 'Offline'}
              </span>
            </div>
          </div>
        </header>

        {/* Center content */}
        <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
          {/* Voice nucleus button (C008) - Center stage */}
          <div className="mb-12">
            <VoiceButton />
          </div>

          {/* Query input */}
          <form onSubmit={handleSubmit} className="w-full max-w-2xl">
            <div className="relative">
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Type or speak your message..."
                className="w-full bg-cell/50 backdrop-blur-sm border border-membrane rounded-2xl px-6 py-4 text-nucleus placeholder-vacuole focus:outline-none focus:border-enzyme focus:ring-2 focus:ring-enzyme/20 transition-all"
              />
              <button
                type="submit"
                disabled={!query.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-enzyme text-void font-semibold rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </form>

          {/* Server-driven UI components (C007) */}
          <div className="w-full max-w-2xl mt-8 space-y-4">
            {values?.ui?.map((ui: any) => (
              <LoadExternalComponent
                key={ui.id}
                message={ui}
                fallback={
                  <div className="bg-cell/50 backdrop-blur-sm border border-membrane rounded-2xl p-6">
                    <div className="animate-pulse text-vacuole">Loading widget...</div>
                  </div>
                }
              />
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
