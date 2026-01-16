"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";

// Types
interface Session {
  id: string;
  title: string;
  work_duration: number;
  break_duration: number;
  status: "running" | "paused" | "completed" | "cancelled";
  remaining_seconds: number;
  current_phase: "work" | "break";
  created_at: string;
  completed_at?: string;
}

interface TimerUpdate {
  type: "tick" | "phase_change" | "completed";
  remaining_seconds: number;
  current_phase: "work" | "break";
  timestamp: string;
}

interface CreateSessionResponse {
  session_id: string;
  title: string;
  work_duration: number;
  break_duration: number;
  status: string;
  remaining_seconds: number;
  current_phase: string;
  created_at: string;
}

export default function Home() {
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003";

  // Form state
  const [title, setTitle] = useState("Focus Session");
  const [workDuration, setWorkDuration] = useState("25");
  const [breakDuration, setBreakDuration] = useState("5");

  // Session state
  const [currentSession, setCurrentSession] = useState<Session | null>(null);
  const [sessionHistory, setSessionHistory] = useState<Session[]>([]);
  const [healthStatus, setHealthStatus] = useState<"checking" | "healthy" | "unhealthy">("checking");
  const [error, setError] = useState<string | null>(null);

  // WebSocket ref
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Calculate progress percentage
  const calculateProgress = (remaining: number, total: number): number => {
    if (total === 0) return 0;
    return ((total - remaining) / total) * 100;
  };

  // Fetch session history
  const fetchHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessionHistory(data.sessions || []);
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  }, [API_URL]);

  // Check backend health
  const checkHealth = useCallback(async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      setHealthStatus(response.ok ? "healthy" : "unhealthy");
    } catch {
      setHealthStatus("unhealthy");
    }
  }, [API_URL]);

  // Connect to WebSocket
  const connectWebSocket = useCallback((sessionId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    const wsUrl = `${API_URL.replace("http", "ws")}/api/v1/ws/timer/${sessionId}`;
    console.log("Connecting to WebSocket:", wsUrl);

    try {
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log("WebSocket connected");
        setError(null);
      };

      wsRef.current.onmessage = (event) => {
        try {
          const update: TimerUpdate = JSON.parse(event.data);
          console.log("WebSocket update:", update);

          setCurrentSession((prev) => {
            if (!prev) return prev;

            if (update.type === "completed") {
              // Session completed - fetch updated history
              fetchHistory();
              return {
                ...prev,
                status: "completed",
                remaining_seconds: 0,
                completed_at: update.timestamp,
              };
            }

            return {
              ...prev,
              remaining_seconds: update.remaining_seconds,
              current_phase: update.current_phase,
              status: update.type === "phase_change" ? "running" : prev.status,
            };
          });
        } catch (err) {
          console.error("Failed to parse WebSocket message:", err);
        }
      };

      wsRef.current.onerror = (event) => {
        console.error("WebSocket error:", event);
        setError("WebSocket connection error");
      };

      wsRef.current.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason);
        if (currentSession?.status === "running") {
          // Attempt to reconnect if session is still running
          console.log("Attempting to reconnect...");
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket(sessionId);
          }, 2000);
        }
      };
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setError("Failed to establish WebSocket connection");
    }
  }, [API_URL, currentSession?.status, fetchHistory]);

  // Disconnect WebSocket
  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      console.log("Disconnecting WebSocket");
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  // Create new session
  const createSession = async () => {
    setError(null);
    try {
      const response = await fetch(`${API_URL}/api/v1/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: title || "Focus Session",
          work_duration: parseInt(workDuration) * 60,
          break_duration: parseInt(breakDuration) * 60,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create session");
      }

      const data: CreateSessionResponse = await response.json();
      const newSession: Session = {
        id: data.session_id,
        title: data.title,
        work_duration: data.work_duration,
        break_duration: data.break_duration,
        status: data.status as Session["status"],
        remaining_seconds: data.remaining_seconds,
        current_phase: data.current_phase as Session["current_phase"],
        created_at: data.created_at,
      };

      setCurrentSession(newSession);
      connectWebSocket(data.session_id);
      fetchHistory();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create session");
    }
  };

  // Start session
  const startSession = async () => {
    if (!currentSession) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/sessions/${currentSession.id}/start`, {
        method: "POST",
      });

      if (response.ok) {
        setCurrentSession((prev) => prev ? { ...prev, status: "running" } : prev);
        connectWebSocket(currentSession.id);
      }
    } catch (err) {
      setError("Failed to start session");
    }
  };

  // Pause session
  const pauseSession = async () => {
    if (!currentSession) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/sessions/${currentSession.id}/pause`, {
        method: "POST",
      });

      if (response.ok) {
        setCurrentSession((prev) => prev ? { ...prev, status: "paused" } : prev);
        disconnectWebSocket();
      }
    } catch (err) {
      setError("Failed to pause session");
    }
  };

  // Resume session
  const resumeSession = async () => {
    if (!currentSession) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/sessions/${currentSession.id}/resume`, {
        method: "POST",
      });

      if (response.ok) {
        setCurrentSession((prev) => prev ? { ...prev, status: "running" } : prev);
        connectWebSocket(currentSession.id);
      }
    } catch (err) {
      setError("Failed to resume session");
    }
  };

  // Cancel session
  const cancelSession = async () => {
    if (!currentSession) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/sessions/${currentSession.id}/cancel`, {
        method: "POST",
      });

      if (response.ok) {
        setCurrentSession((prev) => prev ? { ...prev, status: "cancelled" } : prev);
        disconnectWebSocket();
        fetchHistory();
      }
    } catch (err) {
      setError("Failed to cancel session");
    }
  };

  // Reset form
  const resetForm = () => {
    setCurrentSession(null);
    disconnectWebSocket();
    setError(null);
  };

  // Initial load
  useEffect(() => {
    checkHealth();
    fetchHistory();

    // Cleanup on unmount
    return () => {
      disconnectWebSocket();
    };
  }, [checkHealth, fetchHistory, disconnectWebSocket]);

  // Calculate total duration for progress
  const getTotalDuration = () => {
    if (!currentSession) return 0;
    return currentSession.current_phase === "work"
      ? currentSession.work_duration
      : currentSession.break_duration;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              {process.env.NEXT_PUBLIC_APP_NAME || "Pomodoro Timer"}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Stay focused with timed work sessions
            </p>
          </div>
          <Badge
            variant={healthStatus === "healthy" ? "success" : "destructive"}
            className="text-sm"
          >
            {healthStatus === "checking" ? "Checking..." : healthStatus === "healthy" ? "Backend Online" : "Backend Offline"}
          </Badge>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {!currentSession ? (
          /* Create Session Form */
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle>Create New Session</CardTitle>
              <CardDescription>
                Set up your focus session with custom work and break durations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Session Title</label>
                <Input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g., Deep Work Session"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Work Duration (minutes)
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="120"
                    value={workDuration}
                    onChange={(e) => setWorkDuration(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Break Duration (minutes)
                  </label>
                  <Input
                    type="number"
                    min="1"
                    max="30"
                    value={breakDuration}
                    onChange={(e) => setBreakDuration(e.target.value)}
                  />
                </div>
              </div>

              <Button onClick={createSession} className="w-full" size="lg">
                Start Focus Session
              </Button>
            </CardContent>
          </Card>
        ) : (
          /* Active Session Display */
          <Card className="shadow-lg">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-2xl">{currentSession.title}</CardTitle>
                  <CardDescription>
                    {currentSession.current_phase === "work" ? "Focus Time" : "Break Time"}
                  </CardDescription>
                </div>
                <Badge
                  variant={
                    currentSession.status === "running"
                      ? "success"
                      : currentSession.status === "paused"
                      ? "warning"
                      : currentSession.status === "completed"
                      ? "default"
                      : "destructive"
                  }
                  className="text-sm"
                >
                  {currentSession.status.charAt(0).toUpperCase() + currentSession.status.slice(1)}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Timer Display */}
              <div className="text-center py-8">
                <div className="text-8xl font-bold font-mono tracking-tight text-gray-900 dark:text-white">
                  {formatTime(currentSession.remaining_seconds)}
                </div>
                <div className="mt-4 text-sm text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                  {currentSession.current_phase === "work" ? "Focus" : "Break"} Phase
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <Progress
                  value={calculateProgress(currentSession.remaining_seconds, getTotalDuration())}
                  className="h-3"
                />
                <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                  <span>
                    {currentSession.current_phase === "work" ? "Work" : "Break"} Progress
                  </span>
                  <span>
                    {Math.round(calculateProgress(currentSession.remaining_seconds, getTotalDuration()))}%
                  </span>
                </div>
              </div>

              {/* Control Buttons */}
              <div className="grid grid-cols-2 gap-3">
                {currentSession.status === "running" ? (
                  <Button onClick={pauseSession} variant="outline" size="lg">
                    Pause
                  </Button>
                ) : currentSession.status === "paused" ? (
                  <Button onClick={resumeSession} size="lg">
                    Resume
                  </Button>
                ) : null}

                {currentSession.status !== "completed" && currentSession.status !== "cancelled" && (
                  <Button onClick={cancelSession} variant="destructive" size="lg">
                    Cancel Session
                  </Button>
                )}

                {(currentSession.status === "completed" || currentSession.status === "cancelled") && (
                  <Button onClick={resetForm} variant="outline" size="lg" className="col-span-2">
                    Create New Session
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Session History */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Session History</CardTitle>
            <CardDescription>Your recent focus sessions</CardDescription>
          </CardHeader>
          <CardContent>
            {sessionHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                No sessions yet. Create your first focus session!
              </div>
            ) : (
              <div className="space-y-3">
                {sessionHistory.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-750 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="font-medium text-gray-900 dark:text-white">
                        {session.title}
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {new Date(session.created_at).toLocaleDateString()} ·{" "}
                        {Math.round(session.work_duration / 60)} min work /{" "}
                        {Math.round(session.break_duration / 60)} min break
                      </div>
                    </div>
                    <Badge
                      variant={
                        session.status === "completed"
                          ? "success"
                          : session.status === "cancelled"
                          ? "destructive"
                          : session.status === "running"
                          ? "success"
                          : "warning"
                      }
                    >
                      {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
