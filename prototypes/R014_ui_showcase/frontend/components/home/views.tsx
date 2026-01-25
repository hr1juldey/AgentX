"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { Session } from "@/store/network-store";

/**
 * SessionsView - Displays user's previous conversation sessions
 */
export function SessionsView({ sessions }: { sessions: Session[] }) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Sessions</CardTitle>
          <CardDescription>
            Your previous conversation sessions and generated widgets
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">No sessions yet</p>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => (
                <div
                  key={session.id || session.session_id}
                  className="p-3 border rounded-lg hover:bg-muted cursor-pointer"
                >
                  <h3 className="font-medium">{session.title || session.name || "Untitled Session"}</h3>
                  <p className="text-sm text-muted-foreground">
                    {session.created_at || session.date || "Unknown date"}
                  </p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * ConnectorsView - Configure external service connections
 */
export function ConnectorsView({
  connectors,
  onToggleConnector,
}: {
  connectors: Record<string, boolean>;
  onToggleConnector: (name: string) => void;
}) {
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Connectors</CardTitle>
          <CardDescription>
            Configure external service connections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {Object.entries(connectors).map(([name, connected]) => (
            <div key={name} className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <h3 className="font-medium capitalize">{name}</h3>
                <p className="text-sm text-muted-foreground capitalize">
                  {connected ? "Connected" : "Not connected"}
                </p>
              </div>
              <Button
                variant={connected ? "outline" : "default"}
                onClick={() => onToggleConnector(name)}
              >
                {connected ? "Disconnect" : "Connect"}
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
