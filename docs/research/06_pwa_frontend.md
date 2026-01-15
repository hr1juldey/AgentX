# Progressive Web App (PWA) Frontend Guide

## Overview

AGENTX uses a Progressive Web App (PWA) as its primary client interface, providing native-like experience across all platforms with offline capability and push notifications.

## Why PWA?

### Advantages
- **Cross-platform** - Single codebase for web, mobile, desktop
- **Offline support** - Works without internet
- **Installable** - Add to home screen
- **Push notifications** - Native-like alerts
- **Auto-updates** - Background updates
- **Cost-effective** - 40-60% cheaper than native apps

### Trade-offs
- **Limited hardware access** - Some features restricted
- **Platform differences** - Varying PWA support
- **No app store** - Direct distribution only

## Architecture

### Tech Stack Recommendations

| Category | Technology | Reason |
|----------|-----------|--------|
| Framework | Next.js 15 | React-based, excellent PWA support |
| AI SDK | Vercel AI SDK | Unified API, provider-agnostic, streaming-first |
| UI Library | shadcn/ui | Modern, accessible components |
| State | Zustand | Lightweight, simple |
| Styling | Tailwind CSS | Utility-first, responsive |
| Database | IndexedDB | Local storage for offline |
| API | AI SDK streamText + WebSocket | Streaming with automatic retries |

### Project Structure

```
frontend/
├── app/                    # Next.js app directory
│   ├── api/               # API routes
│   │   ├── chat/          # Chat streaming
│   │   ├── auth/          # Authentication
│   │   └── plugins/       # Plugin management
│   ├── (main)/            # Main layout
│   │   ├── page.tsx       # Dashboard
│   │   ├── chat/          # Chat interface
│   │   ├── settings/      # Settings
│   │   └── profile/       # User profile
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── chat/             # Chat components
│   └── plugins/          # Plugin components
├── lib/                  # Utilities
│   ├── api.ts            # API client
│   ├── store.ts          # Zustand store
│   └── sw.ts             # Service worker
├── public/               # Static assets
│   ├── manifest.json     # PWA manifest
│   ├── icons/            # App icons
│   └── sw.js             # Service worker
└── package.json
```

## Vercel AI SDK Integration

The **Vercel AI SDK** is the recommended TypeScript toolkit for building AGENTX's frontend. It provides a unified API that abstracts away provider-specific details, making it easy to switch between Ollama, OpenAI, Anthropic, Google, and other providers.

### Why Vercel AI SDK for AGENTX?

1. **Provider Agnostic**: Switch between Ollama, OpenAI, Anthropic, Google with a single line change
2. **Streaming First**: Built for real-time token streaming - no more clunky loading states
3. **Tool Calling**: Framework for defining and handling autonomous tool use
4. **Agent Abstraction**: New in SDK 6.0 for reusable agent definitions
5. **Multi-Provider Support**: 50+ providers supported out of the box
6. **Built-in Hooks**: `useChat`, `useCompletion`, `useObject` for common patterns
7. **Error Handling**: Automatic retries, token management, rate limiting awareness

### AI SDK Architecture for AGENTX

The AI SDK has two main libraries:

- **AI SDK Core**: Unified API for generating text, structured objects, tool calls, and building agents
- **AI SDK UI**: Framework-agnostic hooks for building chat and generative user interfaces

```typescript
// Provider-agnostic example with AI SDK
import { generateText } from "ai";
import { ollama } from "@ai-sdk/ollama";

// Works with Ollama (local)
const { text } = await generateText({
  model: ollama("llama3.2"),
  prompt: "What is AGENTX?",
});

// Switch to OpenAI (cloud) - change ONE line
import { openai } from "@ai-sdk/openai";

const { text } = await generateText({
  model: openai("gpt-4o"),
  prompt: "What is AGENTX?",
});
```

### Updated Tech Stack

The frontend should use:

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | Next.js 15 | React Server Components, streaming RSC |
| AI Integration | **Vercel AI SDK** | Unified provider API, streaming, tools |
| Backend Bridge | **@ai-sdk/ollama** | Connect to local Ollama instance |
| Chat UI | AI SDK UI hooks | `useChat`, `useCompletion` |
| Streaming | AI SDK Core | `streamText`, `generateText` |
| Tool Calling | AI SDK Agents | MCP server integration via tools |

### Installation

```bash
npm install ai @ai-sdk/ollama @ai-sdk/openai
# Or for other providers:
# npm install @ai-sdk/anthropic @ai-sdk/google-genai
```

### Core AI SDK Concepts

#### 1. Provider Setup

```typescript
// lib/ai/providers.ts
import { createOpenAI } from "@ai-sdk/openai";
import { createOllama } from "@ai-sdk/ollama";

// Configure multiple providers
export const ollama = createOllama({
  baseURL: "http://localhost:11434",
});

export const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Dynamic provider selection
export function getProvider(providerName: "ollama" | "openai" | "anthropic") {
  switch (providerName) {
    case "ollama":
      return ollama;
    case "openai":
      return openai;
    default:
      return ollama; // Default to local
  }
}
```

#### 2. Streaming Text Generation

```typescript
// app/api/chat/route.ts
import { streamText } from "ai";
import { ollama } from "@ai-sdk/ollama";
import { generateText } from "ai";

export async function POST(req: Request) {
  const { messages, provider = "ollama" } = await req.json();

  // Using AI SDK's streamText for streaming responses
  const result = streamText({
    model: ollama("llama3.2"),
    messages,
    temperature: 0.7,
    maxTokens: 2048,
  });

  // Return the stream directly
  return result.toDataStreamResponse();
}
```

#### 3. Chat Hook (Client-Side)

```typescript
// app/(main)/chat/page.tsx
'use client';

import { useChat } from "ai/react";

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: "/api/chat",

    // Optional: Initial system message
    initialMessages: [
      {
        id: "system",
        role: "system",
        content: "You are AGENTX, a helpful AI assistant with long-term memory."
      }
    ],

    // Handle streaming errors
    onError: (error) => {
      console.error('Chat error:', error);
    },

    // Hook into message completion
    onFinish: (message) => {
      // Store to memory after completion
      storeToMemory(message);
    },
  });

  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <div key={message.id} className={`mb-4 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
            <div className={`inline-block px-4 py-2 rounded-lg ${
              message.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-black'
            }`}>
              {message.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="text-gray-500">AGENTX is thinking...</div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t p-4">
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Type your message..."
          className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="mt-2 w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

function storeToMemory(message: { role: string; content: string }) {
  // Store to Mem0 via API
  fetch('/api/memory', {
    method: 'POST',
    body: JSON.stringify({
      content: message.content,
      role: message.role,
      timestamp: new Date().toISOString()
    })
  });
}
```

#### 4. Tool Calling with MCP Integration

```typescript
// app/api/chat/route.ts
import { streamText } from "ai";
import { ollama } from "@ai-sdk/ollama";
import { tool } from "ai";

// Define MCP tools as AI SDK tools
const searchWeb = tool({
  description: "Search the web for current information",
  parameters: {
    query: {
      type: "string",
      description: "The search query"
    }
  },
  execute: async ({ query }) => {
    // Call SearXNG MCP server
    const response = await fetch(
      `http://192.168.1.4:8080/search?q=${encodeURIComponent(query)}&format=json`
    );
    const results = await response.json();

    return {
      results: results.results?.slice(0, 5).map((r: any) => ({
        title: r.title,
        url: r.url,
        snippet: r.content
      }))
    };
  }
});

const getCompanyData = tool({
  description: "Get company MIS data",
  parameters: {
    metric: {
      type: "string",
      description: "The metric to retrieve (e.g., revenue, expenses)"
    },
    period: {
      type: "string",
      description: "Time period (e.g., current_month, last_quarter)",
      default: "current_month"
    }
  },
  execute: async ({ metric, period }) => {
    // Call Company MIS MCP server
    const response = await fetch('http://localhost:8000/mcp/tools', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: "get_company_data",
        arguments: { metric, period }
      })
    });

    return await response.json();
  }
});

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: ollama("llama3.2"),
    messages,
    tools: {
      searchWeb,
      getCompanyData
    },
    maxSteps: 5, // Allow multi-step reasoning
  });

  return result.toDataStreamResponse();
}
```

#### 5. Generative UI with streamUI (Experimental)

> **Note**: AI SDK RSC (React Server Components) development is currently paused. The team recommends using client-side `useChat` with tool invocations for generative UI.

```typescript
// Experimental: Stream custom UI components
import { streamUI } from "ai/rsc";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamUI({
    model: ollama("llama3.2"),
    messages,

    // Text response
    text: ({ content }) => (
      <div className="ai-message">
        {content}
      </div>
    ),

    // Tool-based UI components
    tools: {
      showChart: tool({
        description: "Display a data chart",
        parameters: {
          data: { type: "array", description: "Chart data" }
        },
        generate: async function* ({ data }) {
          yield <ChartSkeleton />;
          yield <ChartComponent data={data} />;
        }
      }),

      showWeather: tool({
        description: "Show weather information",
        parameters: {
          location: { type: "string", description: "City name" }
        },
        generate: async function* ({ location }) {
          const weather = await getWeather(location);
          yield <WeatherWidget weather={weather} />;
        }
      })
    }
  });

  return result.toDataStreamResponse();
}
```

### AI SDK Best Practices for AGENTX

#### 1. Provider Selection Strategy

```typescript
// lib/ai/config.ts
export const AI_CONFIG = {
  // Use Ollama for privacy-critical operations
  private: "ollama",

  // Use cloud providers for complex reasoning
  reasoning: "anthropic",  // Claude Sonnet 4.5

  // Use fastest for simple queries
  fast: "ollama",

  // Use provider with best vision for images
  vision: "openai",  // GPT-4o
};

export function getModelForTask(task: "chat" | "reasoning" | "vision" | "tools") {
  const provider = AI_CONFIG[task];
  // Return appropriate model based on task
}
```

#### 2. Error Handling with Retries

```typescript
import { generateText } from "ai";
import { ollama } from "@ai-sdk/ollama";

async function robustGeneration(prompt: string, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const { text } = await generateText({
        model: ollama("llama3.2"),
        prompt,
        // AI SDK handles retries automatically for rate limits
      });

      return { success: true, text };

    } catch (error) {
      if (attempt === maxRetries) {
        console.error(`Failed after ${maxRetries} attempts:`, error);
        return {
          success: false,
          error: error.message,
          fallback: "I'm having trouble connecting. Please try again."
        };
      }

      // Exponential backoff
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, attempt) * 1000));
    }
  }
}
```

#### 3. Token Management

```typescript
import { generateText } from "ai";
import { ollama } from "@ai-sdk/ollama";

async function tokenAwareGeneration(messages: any[]) {
  const { text, usage } = await generateText({
    model: ollama("llama3.2"),
    messages,
    // AI SDK tracks usage automatically
  });

  // Log token usage for monitoring
  console.log(`Tokens used: ${usage.totalTokens}`);

  // Warn if approaching context limit
  if (usage.totalTokens > 3000) {
    console.warn("Approaching context limit, consider summarizing");
  }

  return { text, usage };
}
```

### AI SDK + Memory Integration

```typescript
// app/api/chat/route.ts
import { streamText } from "ai";
import { ollama } from "@ai-sdk/ollama";
import Memory from "mem0ai";

const memory = new Memory({
  llm: {
    provider: "ollama",
    config: {
      model: "llama3.2",
      ollama_base_url: "http://localhost:11434"
    }
  }
});

export async function POST(req: Request) {
  const { messages, userId } = await req.json();

  // Retrieve relevant memories
  const lastMessage = messages[messages.length - 1];
  const memories = await memory.search(lastMessage.content, { userId, limit: 3 });

  // Enhance prompt with memory context
  const enhancedMessages = [
    {
      role: "system",
      content: `You are AGENTX. Use the following memories to provide personalized responses:

${memories.results?.map((m: any) => `- ${m.memory}`).join("\n") || "No relevant memories found."}`
    },
    ...messages
  ];

  const result = streamText({
    model: ollama("llama3.2"),
    messages: enhancedMessages,
  });

  // Store interaction to memory
  const fullResponse = await result.text;
  await memory.add(
    `User: ${lastMessage.content}\nAgent: ${fullResponse}`,
    { userId }
  );

  return result.toDataStreamResponse();
}
```

### Performance Benefits

| Feature | Without AI SDK | With AI SDK |
|---------|--------------|-------------|
| **Streaming Setup** | 200+ lines of code | 10 lines with `useChat` |
| **Provider Switch** | Rewrite entire API layer | Change 1 line |
| **Error Handling** | Manual retry logic | Built-in retries |
| **Token Tracking** | Manual counting | Automatic usage tracking |
| **Tool Calling** | Custom implementation | Declarative tool definitions |
| **Multi-Step Agents** | Complex state machines | `maxSteps` parameter |

### References

- [AI SDK Documentation](https://ai-sdk.dev/docs/introduction)
- [AI SDK Core](https://ai-sdk.dev/docs/ai-sdk-core)
- [AI SDK UI](https://ai-sdk.dev/docs/ai-sdk-ui)
- [Vercel AI SDK GitHub](https://github.com/vercel/ai)

---

## Implementation

### 1. PWA Manifest

```json
{
  "name": "AGENTX - Your Personal AI Assistant",
  "short_name": "AGENTX",
  "description": "Memory-enabled AI assistant with temporal RAG",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#000000",
  "orientation": "portrait-primary",
  "scope": "/",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any"
    },
    {
      "src": "/icons/maskable-icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable"
    }
  ],
  "categories": ["productivity", "ai"],
  "shortcuts": [
    {
      "name": "New Chat",
      "short_name": "Chat",
      "description": "Start a new conversation",
      "url": "/chat",
      "icons": [{ "src": "/icons/icon-96x96.png", "sizes": "96x96" }]
    },
    {
      "name": "Settings",
      "short_name": "Settings",
      "description": "Configure AGENTX",
      "url": "/settings",
      "icons": [{ "src": "/icons/icon-96x96.png", "sizes": "96x96" }]
    }
  ]
}
```

### 2. Service Worker

```javascript
// public/sw.js
const CACHE_VERSION = 'v1';
const CACHE_NAME = `agentx-${CACHE_VERSION}`;

// Assets to cache on install
const STATIC_CACHE = [
  '/',
  '/offline',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_CACHE);
    })
  );
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') return;

  // Skip external requests
  if (url.origin !== location.origin) return;

  // API requests - network only
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(
          JSON.stringify({ error: 'Network error', offline: true }),
          {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
          }
        );
      })
    );
    return;
  }

  // Page requests - network first, cache fallback
  event.respondWith(
    fetch(request)
      .then((response) => {
        // Cache successful responses
        if (response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clone);
          });
        }
        return response;
      })
      .catch(() => {
        // Cache fallback
        return caches.match(request).then((cached) => {
          if (cached) return cached;

          // Offline fallback for HTML
          if (request.headers.get('accept')?.includes('text/html')) {
            return caches.match('/offline');
          }
        });
      })
  );
});

// Background sync for messages
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages());
  }
});

async function syncMessages() {
  // Sync offline messages with server
  const messages = await getOfflineMessages();
  for (const message of messages) {
    try {
      await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify(message)
      });
      await removeOfflineMessage(message.id);
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }
}

// Push notifications
self.addEventListener('push', (event) => {
  const options = {
    body: event.data?.text() || 'New message from AGENTX',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/chat'
    },
    actions: [
      {
        action: 'open',
        title: 'Open Chat'
      },
      {
        action: 'dismiss',
        title: 'Dismiss'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('AGENTX', options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  if (event.action === 'open') {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});
```

### 3. Chat Interface

```tsx
// app/(main)/chat/page.tsx
'use client';

import { useState, useEffect, useRef } from 'react';
import { useChatStore } from '@/lib/store';
import { ChatMessage } from '@/components/chat/ChatMessage';
import { ChatInput } from '@/components/chat/ChatInput';
import { TypingIndicator } from '@/components/chat/TypingIndicator';

export default function ChatPage() {
  const {
    messages,
    sendMessage,
    isStreaming,
    connectionStatus
  } = useChatStore();

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-semibold">AGENTX</h1>
          <ConnectionStatus status={connectionStatus} />
        </div>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6">
        {messages.length === 0 ? (
          <WelcomeScreen />
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isStreaming && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="border-t p-4">
        <ChatInput
          onSend={sendMessage}
          disabled={isStreaming || connectionStatus !== 'connected'}
        />
      </div>
    </div>
  );
}

function ConnectionStatus({ status }: { status: string }) {
  const statusConfig = {
    connected: { color: 'text-green-500', text: 'Online' },
    connecting: { color: 'text-yellow-500', text: 'Connecting...' },
    disconnected: { color: 'text-red-500', text: 'Offline' },
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  return (
    <div className={`flex items-center gap-2 ${config.color}`}>
      <div className="w-2 h-2 rounded-full bg-current animate-pulse" />
      <span className="text-sm">{config.text}</span>
    </div>
  );
}
```

### 4. State Management

```typescript
// lib/store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatStore {
  messages: Message[];
  isStreaming: boolean;
  connectionStatus: 'connected' | 'connecting' | 'disconnected';

  // Actions
  sendMessage: (content: string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setConnectionStatus: (status: ChatStore['connectionStatus']) => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      messages: [],
      isStreaming: false,
      connectionStatus: 'disconnected',

      sendMessage: async (content: string) => {
        const { messages } = get();

        // Add user message
        const userMessage: Message = {
          id: Date.now().toString(),
          role: 'user',
          content,
          timestamp: Date.now()
        };

        set((state) => ({
          messages: [...state.messages, userMessage],
          isStreaming: true
        }));

        try {
          // Send to backend
          const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              messages: [...messages, userMessage]
            })
          });

          if (!response.ok) throw new Error('Failed to send');

          // Stream response
          const reader = response.body?.getReader();
          const decoder = new TextDecoder();

          let assistantMessage: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: '',
            timestamp: Date.now()
          };

          set((state) => ({
            messages: [...state.messages, assistantMessage]
          }));

          while (true) {
            const { done, value } = await reader!.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') continue;

                try {
                  const json = JSON.parse(data);
                  if (json.content) {
                    set((state) => {
                      const messages = [...state.messages];
                      messages[messages.length - 1].content += json.content;
                      return { messages };
                    });
                  }
                } catch (e) {
                  // Skip invalid JSON
                }
              }
            }
          }

        } catch (error) {
          console.error('Chat error:', error);

          // Store message for later sync
          await storeOfflineMessage(userMessage);

          set((state) => ({
            isStreaming: false,
            connectionStatus: 'disconnected'
          }));
        } finally {
          set({ isStreaming: false });
        }
      },

      addMessage: (message) => {
        set((state) => ({
          messages: [...state.messages, message]
        }));
      },

      clearMessages: () => {
        set({ messages: [] });
      },

      setConnectionStatus: (status) => {
        set({ connectionStatus: status });
      }
    }),
    {
      name: 'agentx-chat',
      partialize: (state) => ({ messages: state.messages })
    }
  )
);

// Offline storage helpers
async function storeOfflineMessage(message: Message) {
  const db = await openDB();
  await db.add('offline-messages', message);
}

async function getOfflineMessages(): Promise<Message[]> {
  const db = await openDB();
  return await db.getAll('offline-messages');
}

async function openDB() {
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open('agentx', 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains('offline-messages')) {
        db.createObjectStore('offline-messages', { keyPath: 'id' });
      }
    };
  });
}
```

### 5. API Integration

```typescript
// app/api/chat/route.ts
import { NextRequest } from 'next/server';

export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const { messages } = await request.json();

    // Call backend agent
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages })
    });

    if (!response.ok) {
      throw new Error('Backend error');
    }

    // Stream response
    const reader = response.body?.getReader();
    const encoder = new TextEncoder();

    const stream = new ReadableStream({
      async start(controller) {
        try {
          while (true) {
            const { done, value } = await reader!.read();
            if (done) break;

            controller.enqueue(value);
          }
        } catch (error) {
          controller.error(error);
        } finally {
          controller.close();
        }
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      }
    });

  } catch (error) {
    return new Response(
      JSON.stringify({ error: 'Failed to process request' }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    );
  }
}
```

## Best Practices

### 1. Offline-First Design

```typescript
// Check online status
const isOnline = useSyncExternalStore(
  (subscribe) => {
    const handler = () => subscribe();
    window.addEventListener('online', handler);
    window.addEventListener('offline', handler);
    return () => {
      window.removeEventListener('online', handler);
      window.removeEventListener('offline', handler);
    };
  },
  () => navigator.onLine,
  () => true
);

// Show offline indicator
{!isOnline && <OfflineBanner />}
```

### 2. Progressive Enhancement

```typescript
// Feature detection
const supportsServiceWorker = 'serviceWorker' in navigator;
const supportsNotifications = 'Notification' in window;
const supportsWebSocket = 'WebSocket' in window;

// Conditionally enable features
useEffect(() => {
  if (supportsServiceWorker) {
    navigator.serviceWorker.register('/sw.js');
  }

  if (supportsNotifications) {
    Notification.requestPermission();
  }
}, []);
```

### 3. Performance Optimization

```typescript
// Lazy load components
const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  { loading: () => <Skeleton /> }
);

// Image optimization
import Image from 'next/image';

<Image
  src="/avatar.png"
  width={64}
  height={64}
  priority // For above-fold images
/>

// Code splitting
const pluginComponents = {
  vision: () => import('./plugins/Vision'),
  tts: () => import('./plugins/TTS')
};
```

## Deployment

### Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start

# Generate static export
npm run build && npm run export
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
NEXT_PUBLIC_ENABLE_PWA=true
```

## References

- [PWA Specification](https://www.w3.org/TR/appmanifest/)
- [Next.js PWA Documentation](https://nextjs.org/docs/app/building-your-application/optimizations/pwa)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [IndexedDB Guide](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
