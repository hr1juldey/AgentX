"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Mic, Sparkles, User, Bot, StopCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8011";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
        playAudioResponse(data.response);
      } else {
        throw new Error("API request failed");
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioContext = new AudioContext();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        if (audioBuffer.duration >= 0.5) {
          const wavBytes = audioBufferToWav(audioBuffer);
          const uint8Array = new Uint8Array(wavBytes);

          let binary = "";
          const chunkSize = 0x8000;
          for (let i = 0; i < uint8Array.length; i += chunkSize) {
            binary += String.fromCharCode.apply(null, Array.from(uint8Array.subarray(i, i + chunkSize)));
          }
          const base64Audio = btoa(binary);

          await sendVoiceInput(base64Audio);
        }

        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceInput = async (base64Audio: string) => {
    try {
      const ws = new WebSocket("ws://localhost:8011/ws/voice");

      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "audio_chunk", audio_data: base64Audio }));
      };

      let transcript = "";
      let response = "";

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === "transcription") {
          transcript = msg.text;
          setMessages((prev) => [...prev, { role: "user", content: transcript }]);
        } else if (msg.type === "response_chunk") {
          response += msg.text;
          setMessages((prev) => {
            const newMessages = [...prev];
            if (newMessages[newMessages.length - 1]?.role === "assistant") {
              newMessages[newMessages.length - 1].content = response;
            } else {
              newMessages.push({ role: "assistant", content: response });
            }
            return newMessages;
          });
        } else if (msg.type === "audio") {
          playAudioBase64(msg.data);
          ws.close();
        }
      };
    } catch (error) {
      console.error("Voice input error:", error);
    }
  };

  const playAudioResponse = async (text: string) => {
    try {
      const response = await fetch(`${API_URL}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: "en" }),
      });

      if (response.ok) {
        const data = await response.json();
        playAudioBase64(data.audio_data);
      }
    } catch (error) {
      console.error("TTS error:", error);
    }
  };

  const playAudioBase64 = (base64Audio: string) => {
    try {
      const audioBytes = atob(base64Audio);
      const arrayBuffer = new ArrayBuffer(audioBytes.length);
      const view = new Uint8Array(arrayBuffer);
      for (let i = 0; i < audioBytes.length; i++) {
        view[i] = audioBytes.charCodeAt(i);
      }

      const audioContext = new AudioContext();
      audioContext.decodeAudioData(arrayBuffer, (buffer) => {
        const source = audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(audioContext.destination);
        source.start(0);
      });
    } catch (e) {
      console.error("Failed to play audio:", e);
    }
  };

  const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const length = buffer.length * buffer.numberOfChannels * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);

    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, "RIFF");
    view.setUint32(4, length - 8, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, buffer.numberOfChannels, true);
    view.setUint32(24, buffer.sampleRate, true);
    view.setUint32(28, buffer.sampleRate * 2 * buffer.numberOfChannels, true);
    view.setUint16(32, buffer.numberOfChannels * 2, true);
    view.setUint16(34, 16, true);
    writeString(36, "data");
    view.setUint32(40, length - 44, true);

    const offset = 44;
    const channelData = [];
    for (let i = 0; i < buffer.numberOfChannels; i++) {
      channelData.push(buffer.getChannelData(i));
    }

    let index = offset;
    for (let i = 0; i < buffer.length; i++) {
      for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, channelData[channel][i]));
        view.setInt16(index, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
        index += 2;
      }
    }

    return arrayBuffer;
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <main className="h-screen flex flex-col bg-black text-white">
      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center gap-4">
        <div className="bg-white text-black p-2 rounded">
          <Sparkles className="h-5 w-5" />
        </div>
        <div>
          <h1 className="font-semibold text-lg tracking-tight">Assistant</h1>
          <p className="text-xs text-white/50">Powered by DSPy + Ollama</p>
        </div>
      </header>

      {/* Messages */}
      <ScrollArea className="flex-1">
        <div ref={scrollRef} className="max-w-2xl mx-auto py-8 px-6 space-y-8">
          {messages.length === 0 ? (
            <div className="text-center py-32">
              <div className="bg-white text-black p-6 rounded-2xl w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                <Sparkles className="h-10 w-10" />
              </div>
              <h2 className="text-3xl font-semibold mb-3 tracking-tight">How can I help you?</h2>
              <p className="text-white/40 text-sm">I can help with calculations, web searches, and more.</p>
            </div>
          ) : (
            messages.map((message, idx) => (
              <div key={idx} className="flex gap-4">
                <div className={`flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center ${message.role === "user" ? "bg-white/10" : "bg-white text-black"}`}>
                  {message.role === "user" ? <User className="h-5 w-5" /> : <Bot className="h-5 w-5" />}
                </div>
                <div className="flex-1 min-w-0 pt-1">
                  <p className="text-xs font-medium text-white/50 mb-1 uppercase tracking-wider">{message.role === "user" ? "You" : "Assistant"}</p>
                  <p className="text-white/90 whitespace-pre-wrap leading-relaxed">{message.content}</p>
                </div>
              </div>
            ))
          )}

          {isLoading && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-9 h-9 rounded-full bg-white text-black flex items-center justify-center">
                <Bot className="h-5 w-5" />
              </div>
              <div className="flex-1 pt-1">
                <p className="text-xs font-medium text-white/50 mb-2 uppercase tracking-wider">Assistant</p>
                <div className="flex gap-2">
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-white/40 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-white/10 p-4">
        <div className="max-w-2xl mx-auto">
          <div className="flex items-end gap-2 bg-white/5 rounded-2xl border border-white/10 p-3">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Send a message..."
              rows={1}
              className="flex-1 resize-none outline-none bg-transparent text-sm placeholder:text-white/30"
              disabled={isLoading}
            />

            <div className="flex items-center gap-1">
              <Button
                type="button"
                size="icon"
                variant="ghost"
                onClick={toggleRecording}
                disabled={isLoading}
                className={`h-9 w-9 ${isRecording ? "text-red-500 hover:text-red-400" : "text-white/50 hover:text-white"}`}
              >
                {isRecording ? <StopCircle className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
              </Button>

              <Button
                type="button"
                size="icon"
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="h-9 w-9 bg-white text-black hover:bg-white/90 disabled:opacity-30"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <p className="text-xs text-center text-white/30 mt-3">
            {isRecording ? "● Recording... Click stop to send" : "Press Enter to send • Shift+Enter for new line"}
          </p>
        </div>
      </div>
    </main>
  );
}
