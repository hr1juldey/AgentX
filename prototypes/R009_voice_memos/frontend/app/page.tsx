"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, Square, Loader2, Volume2, Trash2, FileAudio } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8009";

interface Memo {
  id: string;
  transcription: string;
  timestamp: number;
}

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [memos, setMemos] = useState<Memo[]>([]);
  const [ttsText, setTtsText] = useState("");
  const [isPlaying, setIsPlaying] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Could not access microphone. Please grant permission.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsProcessing(true);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      const response = await fetch(`${API_URL}/transcribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio_data: base64Audio }),
      });

      if (response.ok) {
        const data = await response.json();
        setMemos((prev) => [
          {
            id: Date.now().toString(),
            transcription: data.text,
            timestamp: Date.now(),
          },
          ...prev,
        ]);
      }
    } catch (error) {
      console.error("Transcription failed:", error);
      alert("Transcription failed. Please try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  const synthesizeSpeech = async () => {
    if (!ttsText.trim()) return;

    setIsPlaying(true);
    try {
      const response = await fetch(`${API_URL}/tts/download`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: ttsText }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.onended = () => {
          setIsPlaying(false);
          URL.revokeObjectURL(audioUrl);
        };
        audio.play();
      }
    } catch (error) {
      console.error("TTS failed:", error);
      alert("Speech synthesis failed. Please try again.");
      setIsPlaying(false);
    }
  };

  const deleteMemo = (id: string) => {
    setMemos((prev) => prev.filter((memo) => memo.id !== id));
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl">
              <FileAudio className="h-8 w-8" />
            </div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-pink-500 bg-clip-text text-transparent">
            Voice Memos
          </h1>
          <p className="text-muted-foreground text-lg">
            Record, transcribe, and synthesize speech
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recording Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mic className="h-5 w-5" />
                Record & Transcribe
              </CardTitle>
              <CardDescription>Record your voice and get instant transcription</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Recording Button */}
              <div className="flex justify-center">
                <Button
                  size="lg"
                  onClick={isRecording ? stopRecording : startRecording}
                  disabled={isProcessing}
                  className={`h-24 w-24 rounded-full ${isRecording ? "bg-destructive hover:bg-destructive/90" : ""}`}
                >
                  {isRecording ? (
                    <Square className="h-10 w-10" />
                  ) : isProcessing ? (
                    <Loader2 className="h-10 w-10 animate-spin" />
                  ) : (
                    <Mic className="h-10 w-10" />
                  )}
                </Button>
              </div>

              <div className="text-center">
                {isRecording && (
                  <div className="flex items-center justify-center gap-2 text-destructive">
                    <div className="w-3 h-3 bg-destructive rounded-full animate-pulse" />
                    <span className="font-medium">Recording...</span>
                  </div>
                )}
                {isProcessing && (
                  <div className="flex items-center justify-center gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Transcribing...</span>
                  </div>
                )}
              </div>

              {/* Memos List */}
              <div className="space-y-3 max-h-[300px] overflow-y-auto">
                {memos.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    No memos yet. Start recording!
                  </p>
                ) : (
                  memos.map((memo) => (
                    <div key={memo.id} className="p-3 border rounded-lg bg-muted/30 group">
                      <p className="text-sm mb-2">{memo.transcription}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-muted-foreground">
                          {new Date(memo.timestamp).toLocaleTimeString()}
                        </span>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-6 w-6 opacity-0 group-hover:opacity-100"
                          onClick={() => deleteMemo(memo.id)}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* TTS Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Volume2 className="h-5 w-5" />
                Text to Speech
              </CardTitle>
              <CardDescription>Convert text to natural speech</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="Enter text to synthesize..."
                value={ttsText}
                onChange={(e) => setTtsText(e.target.value)}
                rows={8}
              />

              <Button
                onClick={synthesizeSpeech}
                disabled={isPlaying || !ttsText.trim()}
                className="w-full gap-2"
              >
                {isPlaying ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Volume2 className="h-4 w-4" />
                )}
                {isPlaying ? "Playing..." : "Speak"}
              </Button>

              <div className="border-t pt-4">
                <p className="text-sm font-medium mb-2">Quick Phrases</p>
                <div className="flex flex-wrap gap-2">
                  {["Hello, how are you?", "This is a test.", "Voice memos are awesome!"].map((phrase) => (
                    <Badge
                      key={phrase}
                      variant="secondary"
                      className="cursor-pointer hover:bg-secondary/70"
                      onClick={() => setTtsText(phrase)}
                    >
                      {phrase}
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
}
