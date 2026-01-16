"use client";

import { useEffect, useRef, useCallback, useState } from "react";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8011/ws/voice";

export type WSMessage =
  | { type: "connected"; session_id: string }
  | { type: "transcription"; text: string }
  | { type: "thinking" }
  | { type: "response_start" }
  | { type: "response_chunk"; text: string }
  | { type: "audio"; data: string }
  | { type: "listening" }
  | { type: "pong" }
  | { type: "error"; message: string };

export interface UseVoiceReturn {
  isConnected: boolean;
  isListening: boolean;
  isThinking: boolean;
  currentTranscript: string;
  currentResponse: string;
  connect: () => void;
  disconnect: () => void;
  sendAudio: (audioData: string) => void;
}

export function useWebSocket(): UseVoiceReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState("");
  const [currentResponse, setCurrentResponse] = useState("");

  const wsRef = useRef<WebSocket | null>(null);
  const responseBufferRef = useRef("");

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);

        switch (msg.type) {
          case "connected":
            console.log("Session:", msg.session_id);
            break;

          case "transcription":
            setCurrentTranscript(msg.text);
            break;

          case "thinking":
            setIsThinking(true);
            responseBufferRef.current = "";
            setCurrentResponse("");
            break;

          case "response_start":
            responseBufferRef.current = "";
            break;

          case "response_chunk":
            responseBufferRef.current += msg.text;
            setCurrentResponse(responseBufferRef.current);
            break;

          case "audio":
            // Play audio
            playAudio(msg.data);
            setIsThinking(false);
            break;

          case "listening":
            setIsListening(true);
            break;

          case "error":
            console.error("WebSocket error:", msg.message);
            break;
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
      setIsListening(false);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsRef.current = ws;
  }, []);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
  }, []);

  const sendAudio = useCallback((audioData: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "audio_chunk",
        audio_data: audioData
      }));
    }
  }, []);

  // Play Base64 audio
  const playAudio = (base64Audio: string) => {
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

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  return {
    isConnected,
    isListening,
    isThinking,
    currentTranscript,
    currentResponse,
    connect,
    disconnect,
    sendAudio,
  };
}
