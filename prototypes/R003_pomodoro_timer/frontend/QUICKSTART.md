# R003 Pomodoro Timer - Quick Start Guide

## Prerequisites
- Node.js 18+ installed
- Backend running on `http://localhost:8003`
- WebSocket endpoint available at `/api/v1/ws/timer/{session_id}`

## Installation

```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R003_pomodoro_timer/frontend
npm install
```

## Development

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## Production Build

```bash
npm run build
npm start
```

## WebSocket Connection Test

### Test WebSocket Connection Directly
```bash
# Install wscat
npm install -g wscat

# Connect to a test session
wscat -c ws://localhost:8003/api/v1/ws/timer/test-session-id

# You should see messages like:
# {"type":"tick","remaining_seconds":1499,"current_phase":"work","timestamp":"2025-01-16T03:00:00Z"}
```

## Features

### 1. Create Session
- Enter session title (default: "Focus Session")
- Set work duration (1-120 minutes, default: 25)
- Set break duration (1-30 minutes, default: 5)
- Click "Start Focus Session"

### 2. Real-Time Timer Display
- Large countdown (MM:SS format)
- Updates every second via WebSocket
- Phase indicator (Work/Break)
- Progress bar showing completion percentage

### 3. Session Controls
- **Start**: Begin session and connect WebSocket
- **Pause**: Stop timer and disconnect WebSocket
- **Resume**: Continue timer and reconnect WebSocket
- **Cancel**: End session and close connection

### 4. Session History
- View all completed sessions
- Shows title, date, durations, and status
- Auto-refreshes when session completes

### 5. Backend Health Indicator
- Green badge: Backend is online
- Red badge: Backend is offline
- Auto-checks on page load

## WebSocket Implementation

### Connection URL
```
ws://localhost:8003/api/v1/ws/timer/{session_id}
```

### Message Types
1. **tick**: Timer update every second
2. **phase_change**: Work → Break or Break → Work
3. **completed**: Session finished

### Message Format
```json
{
  "type": "tick",
  "remaining_seconds": 1499,
  "current_phase": "work",
  "timestamp": "2025-01-16T03:00:00Z"
}
```

### Reconnection Logic
- Auto-reconnects after 2 seconds if connection drops
- Only reconnects if session status is "running"
- Prevents reconnection loops on pause/complete

## Troubleshooting

### WebSocket Connection Fails
1. Check backend is running: `curl http://localhost:8003/health`
2. Verify WebSocket endpoint exists in backend
3. Check browser console for WebSocket errors
4. Ensure no firewall blocking port 8003

### Timer Not Updating
1. Check browser console for WebSocket messages
2. Verify session is in "running" status
3. Check backend logs for timer events
4. Try refreshing the page

### Session History Not Updating
1. Check browser console for API errors
2. Verify GET `/api/v1/sessions` endpoint works
3. Check network tab in DevTools

## File Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main page (525 lines, WebSocket logic)
├── components/ui/
│   ├── badge.tsx            # Status badges (NEW)
│   ├── button.tsx           # Button components
│   ├── card.tsx             # Card layouts
│   ├── input.tsx            # Form inputs
│   └── progress.tsx         # Progress bar (NEW)
├── lib/
│   └── utils.ts             # Utility functions
├── scripts/
│   └── dev.sh               # Development script
├── .env.local               # Environment variables
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript config
├── next.config.js           # Next.js config
├── tailwind.config.js       # Tailwind CSS config
└── README_IMPLEMENTATION.md # Detailed implementation docs
```

## Key Differences from R002

| Feature | R002 (Todo) | R003 (Pomodoro) |
|---------|-------------|-----------------|
| Real-time | Polling (5s) | WebSocket (1s) |
| Updates | Manual refresh | Auto-update |
| State | Basic status | Countdown timer |
| Network | REST only | REST + WebSocket |

## Next Steps

### Level 3 Enhancements
- [ ] Circular timer visualization (SVG)
- [ ] Sound notifications
- [ ] Browser notifications
- [ ] Session statistics
- [ ] Custom themes
- [ ] Multiple concurrent sessions

## API Endpoints Used

### REST
- `POST /api/v1/sessions` - Create session
- `POST /api/v1/sessions/{id}/start` - Start session
- `POST /api/v1/sessions/{id}/pause` - Pause session
- `POST /api/v1/sessions/{id}/resume` - Resume session
- `POST /api/v1/sessions/{id}/cancel` - Cancel session
- `GET /api/v1/sessions` - List sessions
- `GET /health` - Health check

### WebSocket
- `ws://localhost:8003/api/v1/ws/timer/{session_id}` - Timer updates
