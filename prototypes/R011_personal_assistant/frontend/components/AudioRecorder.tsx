"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface AudioRecorderProps {
  isConnected: boolean;
  isListening: boolean;
  onAudioData: (base64Audio: string) => void;
}

export function AudioRecorder({ isConnected, isListening, onAudioData }: AudioRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number | null>(null);

  // Start recording
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Setup audio context for visualization
      const audioContext = new AudioContext();
      const analyser = audioContext.createAnalyser();
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      analyser.fftSize = 256;

      audioContextRef.current = audioContext;
      analyserRef.current = analyser;

      // Setup MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
        audioBitsPerSecond: 16000
      });

      mediaRecorderRef.current = mediaRecorder;

      // Accumulate audio chunks and send every 3 seconds
      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.push(event.data);
        }
      };

      // Send accumulated audio every 3 seconds
      const sendInterval = setInterval(async () => {
        if (audioChunks.length > 0 && isRecording) {
          // Combine all chunks
          const combinedBlob = new Blob(audioChunks, { type: "audio/webm" });
          audioChunks.length = 0; // Clear array

          try {
            const arrayBuffer = await combinedBlob.arrayBuffer();

            // Convert to WAV format for Silero STT
            const audioContext = new AudioContext();
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

            // Only send if we have enough audio (at least 2 seconds)
            if (audioBuffer.duration >= 2.0) {
              const wavBytes = audioBufferToWav(audioBuffer);
              const uint8Array = new Uint8Array(wavBytes);

              // Convert to base64 using chunks to avoid stack overflow
              let binary = '';
              const chunkSize = 0x8000;
              for (let i = 0; i < uint8Array.length; i += chunkSize) {
                binary += String.fromCharCode.apply(null, Array.from(uint8Array.subarray(i, i + chunkSize)));
              }
              const base64Audio = btoa(binary);

              onAudioData(base64Audio);
            }
          } catch (error) {
            console.error("Error processing audio:", error);
          }
        }
      }, 3000);

      // Store interval for cleanup
      (mediaRecorder as any)._sendInterval = sendInterval;

      mediaRecorder.start(1000); // Request chunks every 1 second
      setIsRecording(true);
      updateAudioLevel();

    } catch (error) {
      console.error("Error starting recording:", error);
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      // Clear the send interval
      const interval = (mediaRecorderRef.current as any)._sendInterval;
      if (interval) clearInterval(interval);

      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
    }

    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }

    setIsRecording(false);
    setAudioLevel(0);
  };

  // Update audio level for visualization
  const updateAudioLevel = () => {
    if (analyserRef.current) {
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
      analyserRef.current.getByteFrequencyData(dataArray);

      const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
      setAudioLevel(average / 255);

      animationRef.current = requestAnimationFrame(updateAudioLevel);
    }
  };

  // Convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer: AudioBuffer): ArrayBuffer => {
    const length = buffer.length * buffer.numberOfChannels * 2 + 44;
    const arrayBuffer = new ArrayBuffer(length);
    const view = new DataView(arrayBuffer);

    // WAV header
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

    // Audio data
    const offset = 44;
    const channelData = [];
    for (let i = 0; i < buffer.numberOfChannels; i++) {
      channelData.push(buffer.getChannelData(i));
    }

    let index = offset;
    for (let i = 0; i < buffer.length; i++) {
      for (let channel = 0; channel < buffer.numberOfChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, channelData[channel][i]));
        view.setInt16(index, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        index += 2;
      }
    }

    return arrayBuffer;
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopRecording();
    };
  }, []);

  return (
    <div className="flex items-center gap-4">
      <Button
        onClick={isRecording ? stopRecording : startRecording}
        disabled={!isConnected}
        size="lg"
        variant={isRecording ? "destructive" : "default"}
        className="relative"
      >
        {isRecording ? (
          <>
            <MicOff className="h-5 w-5 mr-2" />
            Stop
          </>
        ) : (
          <>
            <Mic className="h-5 w-5 mr-2" />
            {isListening ? "Speak" : "Connect"}
          </>
        )}
      </Button>

      {isRecording && (
        <div className="flex items-center gap-2">
          <div className="w-32 h-2 bg-secondary rounded-full overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-75"
              style={{ width: `${audioLevel * 100}%` }}
            />
          </div>
          <Badge variant="secondary">Recording (sends every 3s)</Badge>
        </div>
      )}

      {!isConnected && (
        <Badge variant="outline" className="gap-1">
          <Loader2 className="h-3 w-3 animate-spin" />
          Connecting...
        </Badge>
      )}

      {isConnected && !isRecording && (
        <Badge variant="outline" className="gap-1">
          <div className="w-2 h-2 bg-green-500 rounded-full" />
          {isListening ? "Ready" : "Busy"}
        </Badge>
      )}
    </div>
  );
}
