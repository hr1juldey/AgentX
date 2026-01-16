"use client";

import { useEffect, useState } from "react";
import { Monitor, Smartphone, Tablet, LogOut, Shield, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getRelativeTime } from "@/lib/utils";

type DeviceType = "desktop" | "mobile" | "tablet";

interface Session {
  id: string;
  device_name: string;
  device_type: DeviceType;
  last_active: string;
  ip_address: string;
  is_current: boolean;
  is_active: boolean;
}

const deviceIcons = {
  desktop: Monitor,
  mobile: Smartphone,
  tablet: Tablet,
};

export default function Home() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [currentTime, setCurrentTime] = useState<Date>(new Date());
  const [isLoading, setIsLoading] = useState(true);

  // Fetch sessions from API
  const fetchSessions = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8006";
      const response = await fetch(`${apiUrl}/api/sessions`);
      if (response.ok) {
        const data = await response.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error("Failed to fetch sessions:", error);
      // Use mock data for development
      setSessions(mockSessions);
    } finally {
      setIsLoading(false);
    }
  };

  // Logout a specific session
  const logoutSession = async (sessionId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8006";
      const response = await fetch(`${apiUrl}/api/sessions/${sessionId}`, {
        method: "DELETE",
      });
      if (response.ok) {
        setSessions(sessions.filter((s) => s.id !== sessionId));
      }
    } catch (error) {
      console.error("Failed to logout session:", error);
    }
  };

  // Logout all sessions except current
  const logoutAllSessions = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8006";
      const response = await fetch(`${apiUrl}/api/sessions`, {
        method: "DELETE",
      });
      if (response.ok) {
        const currentSession = sessions.find((s) => s.is_current);
        setSessions(currentSession ? [currentSession] : []);
      }
    } catch (error) {
      console.error("Failed to logout all sessions:", error);
    }
  };

  // Update current time every second for relative time display
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Fetch sessions on mount and refresh every 30 seconds
  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 30000);
    return () => clearInterval(interval);
  }, []);

  const activeSessions = sessions.filter((s) => s.is_active);
  const otherSessionsCount = activeSessions.length - 1;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 p-4 md:p-8">
      <div className="max-w-5xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <h1 className="text-3xl font-bold tracking-tight">Session Manager</h1>
            <p className="text-muted-foreground">
              Manage your active sessions across all devices
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Shield className="h-8 w-8 text-primary" />
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
              <Monitor className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeSessions.length}</div>
              <p className="text-xs text-muted-foreground">
                {otherSessionsCount > 0 ? `${otherSessionsCount} other device${otherSessionsCount > 1 ? 's' : ''}` : "No other devices"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Device</CardTitle>
              <Smartphone className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {sessions.find((s) => s.is_current)?.device_name || "Unknown"}
              </div>
              <p className="text-xs text-muted-foreground">
                {sessions.find((s) => s.is_current)?.ip_address || "Unknown IP"}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {currentTime.toLocaleTimeString()}
              </div>
              <p className="text-xs text-muted-foreground">
                Auto-refreshes every 30s
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Sessions Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Active Sessions</CardTitle>
                <CardDescription>
                  View and manage all your active device sessions
                </CardDescription>
              </div>
              {activeSessions.length > 1 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={logoutAllSessions}
                  className="gap-2"
                >
                  <LogOut className="h-4 w-4" />
                  Logout All Sessions
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                Loading sessions...
              </div>
            ) : activeSessions.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No active sessions found
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Last Active</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeSessions.map((session) => {
                    const DeviceIcon = deviceIcons[session.device_type];
                    return (
                      <TableRow key={session.id}>
                        <TableCell className="font-medium">
                          <div className="flex items-center gap-2">
                            <DeviceIcon className="h-4 w-4 text-muted-foreground" />
                            <span>{session.device_name}</span>
                            {session.is_current && (
                              <Badge variant="secondary" className="text-xs">
                                Current
                              </Badge>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {session.device_type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          {getRelativeTime(session.last_active)}
                        </TableCell>
                        <TableCell className="font-mono text-sm">
                          {session.ip_address}
                        </TableCell>
                        <TableCell>
                          <Badge variant={session.is_active ? "success" : "secondary"}>
                            {session.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          {!session.is_current && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => logoutSession(session.id)}
                              className="gap-2 hover:text-destructive"
                            >
                              <LogOut className="h-4 w-4" />
                              Logout
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Security Notice */}
        <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-900 dark:bg-yellow-950">
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Security Notice
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <p>
              Regularly review your active sessions to ensure your account security.
              If you notice any unfamiliar devices or locations, immediately log them out
              and consider changing your password.
            </p>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}

// Mock data for development
const mockSessions: Session[] = [
  {
    id: "1",
    device_name: "MacBook Pro",
    device_type: "desktop",
    last_active: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    ip_address: "192.168.1.4",
    is_current: true,
    is_active: true,
  },
  {
    id: "2",
    device_name: "iPhone 15 Pro",
    device_type: "mobile",
    last_active: new Date(Date.now() - 15 * 60 * 1000).toISOString(),
    ip_address: "192.168.1.105",
    is_current: false,
    is_active: true,
  },
  {
    id: "3",
    device_name: "iPad Air",
    device_type: "tablet",
    last_active: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    ip_address: "192.168.1.112",
    is_current: false,
    is_active: true,
  },
  {
    id: "4",
    device_name: "Windows Desktop",
    device_type: "desktop",
    last_active: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    ip_address: "192.168.1.78",
    is_current: false,
    is_active: false,
  },
];
