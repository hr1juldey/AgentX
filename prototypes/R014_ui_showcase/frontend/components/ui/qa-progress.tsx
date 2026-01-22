"use client"

import { Card, CardHeader, CardTitle, CardContent } from "./card"
import { Loader2, CheckCircle, XCircle } from "lucide-react"
import { memo } from "react"

type QACheckpointStatus = "running" | "passed" | "failed"
type QACheckpoint = {
  status: QACheckpointStatus
  checkpoint: string
  details: Record<string, unknown>
}

interface QAProgressProps {
  checkpoints: Record<string, QACheckpoint>
}

export const QAProgressDisplay = memo(function QAProgress({ checkpoints }: QAProgressProps) {
  const entries = Object.entries(checkpoints)
  if (entries.length === 0) return null

  return (
    <Card className="mb-4">
      <CardHeader>
        <CardTitle className="text-sm">Pipeline Progress</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {entries.map(([checkpoint, { status, details }]) => (
            <div key={checkpoint} className="flex items-center gap-2 text-sm">
              {status === "running" && <Loader2 className="w-4 h-4 animate-spin" />}
              {status === "passed" && <CheckCircle className="w-4 h-4 text-green-500" />}
              {status === "failed" && <XCircle className="w-4 h-4 text-red-500" />}
              <span className="capitalize">{checkpoint.replace(/_/g, " ")}</span>
              <span className="text-muted-foreground text-xs">
                ({status})
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
})
