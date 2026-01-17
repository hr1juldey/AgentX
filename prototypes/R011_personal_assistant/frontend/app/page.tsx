"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Sparkles, Mic, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { AudioRecorder } from "@/components/AudioRecorder";
import { useWebSocket } from "@/hooks/useWebSocket";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8011";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: number;
}

type VoiceMode = "voice" | "text";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: "Hello! I'm your AI personal assistant. I can help with calculations, searches, and weather queries. How can I assist you today?", timestamp: Date.now() }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [voiceMode, setVoiceMode] = useState<VoiceMode>("text");
  const scrollRef = useRef<HTMLDivElement>(null);

  // WebSocket for voice mode
  const {
    isConnected: wsConnected,
    isListening,
    isThinking,
    currentTranscript,
    currentResponse,
    connect: wsConnect,
    disconnect: wsDisconnect,
    sendAudio,
  } = useWebSocket();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, currentResponse]);

  // Auto-connect WebSocket in voice mode
  useEffect(() => {
    if (voiceMode === "voice" && !wsConnected) {
      wsConnect();
    } else if (voiceMode === "text" && wsConnected) {
      wsDisconnect();
    }

    return () => {
      if (wsConnected) wsDisconnect();
    };
  }, [voiceMode, wsConnected, wsConnect, wsDisconnect]);

  // Add voice conversation to messages when complete
  useEffect(() => {
    if (currentTranscript && !isThinking) {
      setMessages((prev) => [
        ...prev,
        { role: "user", content: currentTranscript, timestamp: Date.now() }
      ]);
    }

    if (currentResponse && !isThinking) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: currentResponse, timestamp: Date.now() }
      ]);
    }
  }, [isThinking, currentTranscript, currentResponse]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: "user", content: input, timestamp: Date.now() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input, conversation_id: conversationId }),
      });

      if (response.ok) {
        const data = await response.json();
        setConversationId(data.conversation_id);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.response, timestamp: Date.now() }
        ]);
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error. Please try again.", timestamp: Date.now() }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50 dark:from-emerald-950 dark:to-teal-950">
      <div className="container mx-auto px-4 py-8 max-w-4xl h-screen flex flex-col">
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl"><Sparkles className="h-8 w-8" /></div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-teal-500 bg-clip-text text-transparent">
            Personal Assistant
          </h1>
          <p className="text-muted-foreground">
            {voiceMode === "voice"
              ? "Voice conversation mode - Speak naturally"
              : "AI-powered agent with ReAct reasoning and tool use"}
          </p>
        </div>

        <Card className="flex-1 flex flex-col overflow-hidden">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {voiceMode === "voice" ? "Voice Chat" : "Chat"}
                </CardTitle>
                <CardDescription>
                  {voiceMode === "voice"
                    ? "Click the microphone button and start speaking"
                    : "Ask me anything - I can use tools to help you"}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className="gap-1">
                  <div className={`w-2 h-2 rounded-full ${voiceMode === "voice" && wsConnected ? "bg-green-500" : "bg-yellow-500"}`} />
                  {voiceMode === "voice" ? (wsConnected ? "Voice Ready" : "Connecting...") : "Online"}
                </Badge>
              </div>
            </div>

            {/* Mode toggle */}
            <div className="flex gap-2 mt-4">
              <Button
                variant={voiceMode === "text" ? "default" : "outline"}
                size="sm"
                onClick={() => setVoiceMode("text")}
                className="flex-1"
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Text Mode
              </Button>
              <Button
                variant={voiceMode === "voice" ? "default" : "outline"}
                size="sm"
                onClick={() => setVoiceMode("voice")}
                className="flex-1"
              >
                <Mic className="h-4 w-4 mr-2" />
                Voice Mode
              </Button>
            </div>
          </CardHeader>

          <CardContent className="flex-1 flex flex-col p-0">
            <ScrollArea className="flex-1 px-6">
              <div ref={scrollRef} className="space-y-4 py-4">
                {messages.map((message, idx) => (
                  <div key={idx} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`flex gap-3 max-w-[80%] ${message.role === "user" ? "flex-row-reverse" : ""}`}>
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${message.role === "user" ? "bg-primary" : "bg-secondary"}`}>
                        {message.role === "user" ? <User className="h-4 w-4 text-primary-foreground" /> : <Bot className="h-4 w-4 text-secondary-foreground" />}
                      </div>
                      <div className={`rounded-lg px-4 py-2 ${message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <span className="text-xs opacity-70 mt-1 block" suppressHydrationWarning>{new Date(message.timestamp).toLocaleTimeString()}</span>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Voice mode: Show current interaction */}
                {voiceMode === "voice" && (currentTranscript || isThinking || currentResponse) && (
                  <>
                    {currentTranscript && !isThinking && (
                      <div className="flex justify-end">
                        <div className="flex gap-3 max-w-[80%] flex-row-reverse">
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                            <User className="h-4 w-4 text-primary-foreground" />
                          </div>
                          <div className="rounded-lg px-4 py-2 bg-primary text-primary-foreground">
                            <p className="text-sm whitespace-pre-wrap">{currentTranscript}</p>
                            <span className="text-xs opacity-70 mt-1 block" suppressHydrationWarning>Just now</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {isThinking && (
                      <div className="flex justify-start">
                        <div className="flex gap-3">
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                            <Bot className="h-4 w-4 text-secondary-foreground" />
                          </div>
                          <div className="rounded-lg px-4 py-2 bg-muted">
                            <Loader2 className="h-4 w-4 animate-spin" />
                          </div>
                        </div>
                      </div>
                    )}

                    {currentResponse && !isThinking && (
                      <div className="flex justify-start">
                        <div className="flex gap-3">
                          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                            <Bot className="h-4 w-4 text-secondary-foreground" />
                          </div>
                          <div className="rounded-lg px-4 py-2 bg-muted">
                            <p className="text-sm whitespace-pre-wrap">{currentResponse}</p>
                            <span className="text-xs opacity-70 mt-1 block" suppressHydrationWarning>Just now</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}

                {/* Text mode: Loading indicator */}
                {voiceMode === "text" && isLoading && (
                  <div className="flex justify-start">
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                        <Bot className="h-4 w-4 text-secondary-foreground" />
                      </div>
                      <div className="rounded-lg px-4 py-2 bg-muted">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* Input area */}
            <div className="p-4 border-t">
              {voiceMode === "text" ? (
                <form onSubmit={(e) => { e.preventDefault(); sendMessage(); }} className="flex gap-2">
                  <Input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button type="submit" disabled={isLoading || !input.trim()} size="icon">
                    {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                  </Button>
                </form>
              ) : (
                <AudioRecorder
                  isConnected={wsConnected}
                  isListening={isListening}
                  onAudioData={sendAudio}
                />
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
