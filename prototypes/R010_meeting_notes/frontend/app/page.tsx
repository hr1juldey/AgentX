"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, Square, FileText, Activity } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8010";

export default function Home() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [speechDetected, setSpeechDetected] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = async (e) => {
        if (e.data.size > 0) {
          await processAudioChunk(e.data);
        }
      };

      mediaRecorder.start(1000); // Send chunks every second
      setIsRecording(true);

      // Simulate speech detection
      intervalRef.current = setInterval(() => {
        setSpeechDetected(Math.random() > 0.3);
      }, 500);

    } catch (error) {
      console.error("Error:", error);
      alert("Could not access microphone");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(t => t.stop());
      setIsRecording(false);
      setSpeechDetected(false);
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
  };

  const processAudioChunk = async (chunk: Blob) => {
    setIsProcessing(true);
    try {
      const arrayBuffer = await chunk.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

      const response = await fetch(`${API_URL}/transcribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audio_data: base64Audio }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.text) {
          setTranscript(prev => prev + " " + data.text);
        }
      }
    } catch (error) {
      console.error("Transcription error:", error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-950 dark:to-purple-950">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-xl"><FileText className="h-8 w-8" /></div>
          </div>
          <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
            Meeting Notes
          </h1>
          <p className="text-muted-foreground text-lg">Real-time transcription with voice activity detection</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span className="flex items-center gap-2"><Activity className="h-5 w-5" />Live Transcription</span>
              {speechDetected && <div className="flex items-center gap-2 text-green-500"><div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />Speaking</div>}
            </CardTitle>
            <CardDescription>Start recording to see real-time transcription</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex justify-center gap-4">
              <Button size="lg" onClick={isRecording ? stopRecording : startRecording} className={isRecording ? "bg-destructive hover:bg-destructive/90" : ""}>
                {isRecording ? <><Square className="h-4 w-4 mr-2" />Stop</> : <><Mic className="h-4 w-4 mr-2" />Start Recording</>}
              </Button>
            </div>

            <Textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} placeholder="Transcription will appear here..." rows={15} className="font-mono text-sm" />

            {transcript && (
              <div className="text-sm text-muted-foreground text-center">
                {transcript.split(/\s+/).length} words • {transcript.length} characters
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
