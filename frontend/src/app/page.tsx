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
import { useStream } from '@/hooks/useLangGraph';
import { LoadExternalComponent } from '@/components/ui/LoadExternalComponent';

import { tokens } from '@/lib/design-tokens';
import { MetaballBackground } from '@/components/metaball-canvas';
import { VoiceButton } from '@/components/voice-button';
import { useWebSocket } from '@/hooks/useWebSocket';

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

  // WebSocket connection for real-time updates
  const { isConnected, sendMessage, messages } = useWebSocket(
    'ws://localhost:2024/api/v1/ws'
  );

  // LangGraph stream integration (C007)
  const { thread, values } = useStream({
    apiUrl: 'http://localhost:2024',
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
      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-nucleus mb-2">
            Real AgentX v0.1
          </h1>
          <p className="text-cytoplasm">
            LangGraph Server-Driven UI + Organic Design System
          </p>
        </header>

        {/* Connection status */}
        <div className="mb-4 flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-golgi' : 'bg-lysosome'
            }`}
          />
          <span className="text-sm text-cytoplasm">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>

        {/* Query input */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask me anything..."
              className="flex-1 bg-membrane border border-membrane rounded-lg px-4 py-3 text-nucleus placeholder-vacuole focus:outline-none focus:border-enzyme"
            />
            <button
              type="submit"
              className="px-6 py-3 bg-enzyme text-void font-semibold rounded-lg hover:opacity-90 transition-opacity"
            >
              Send
            </button>
          </div>
        </form>

        {/* Voice nucleus button (C008) */}
        <div className="mb-8 flex justify-center">
          <VoiceButton />
        </div>

        {/* Server-driven UI components (C007) */}
        <div className="space-y-4">
          {values?.ui?.map((ui: any) => (
            <LoadExternalComponent
              key={ui.id}
              message={ui}
              fallback={
                <div className="bg-cell border border-membrane rounded-lg p-4">
                  <div className="animate-pulse text-vacuole">Loading widget...</div>
                </div>
              }
            />
          ))}
        </div>

        {/* WebSocket messages */}
        {messages.length > 0 && (
          <div className="mt-8 space-y-2">
            <h2 className="text-xl font-semibold text-nucleus mb-4">Messages</h2>
            {messages.map((msg, index) => (
              <div
                key={index}
                className="bg-cell border border-membrane rounded-lg p-4"
              >
                <pre className="text-sm text-cytoplasm overflow-x-auto">
                  {JSON.stringify(msg, null, 2)}
                </pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
