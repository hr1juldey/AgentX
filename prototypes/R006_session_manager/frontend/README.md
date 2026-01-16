# Session Manager Frontend

Level 3 Next.js frontend for managing user sessions across multiple devices.

## Features

- **Session List Display**: View all active sessions with device information
- **Device Type Icons**: Visual indicators for desktop, mobile, and tablet devices
- **Relative Time Display**: Shows "2 minutes ago", "5 hours ago", etc.
- **Active Status Badges**: Color-coded status indicators
- **Current Session Indicator**: Highlights the current device
- **Per-Session Logout**: Logout individual sessions
- **Logout All**: One-click to logout all other sessions
- **Auto-Refresh**: Automatically refreshes session data every 30 seconds
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (Button, Card, Badge, Table)
- **Icons**: Lucide React
- **Language**: TypeScript

## Project Structure

```
frontend/
├── app/
│   ├── globals.css          # Global styles with CSS variables
│   ├── layout.tsx           # Root layout with metadata
│   └── page.tsx             # Main session list page
├── components/
│   └── ui/
│       ├── badge.tsx        # Status badge component
│       ├── button.tsx       # Button component with variants
│       ├── card.tsx         # Card components
│       └── table.tsx        # Table components for session list
├── lib/
│   └── utils.ts             # Utility functions (cn, getRelativeTime)
├── scripts/
│   └── setup.sh             # Setup script for dependency installation
├── .env.local               # Environment variables (API URL)
├── .env.local.example       # Environment template
├── .gitignore               # Git ignore rules
├── next.config.js           # Next.js configuration
├── package.json             # Dependencies and scripts
├── postcss.config.js        # PostCSS configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── tsconfig.json            # TypeScript configuration
```

## Setup

### Prerequisites

- Node.js 18+ installed
- Backend API running on port 8006

### Quick Start

```bash
# Run the setup script
./scripts/setup.sh

# Or manually install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3006`

## Environment Variables

Create `.env.local` from `.env.local.example`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8006
NEXT_PUBLIC_APP_NAME=Session Manager
```

## API Integration

The frontend expects the following API endpoints:

### GET `/api/sessions`
Returns list of active sessions

```json
{
  "sessions": [
    {
      "id": "string",
      "device_name": "string",
      "device_type": "desktop" | "mobile" | "tablet",
      "last_active": "ISO8601 timestamp",
      "ip_address": "string",
      "is_current": boolean,
      "is_active": boolean
    }
  ]
}
```

### DELETE `/api/sessions/:id`
Logout a specific session

### DELETE `/api/sessions`
Logout all sessions except current

## UI Components

### Session List Table
- **Device Column**: Shows device name with icon and "Current" badge if applicable
- **Type Column**: Device type badge (Desktop/Mobile/Tablet)
- **Last Active Column**: Relative time display
- **IP Address Column**: IP address in monospace font
- **Status Column**: Active/Inactive badge
- **Actions Column**: Logout button (hidden for current session)

### Stats Cards
- Active Sessions count
- Current Device info
- Last Updated timestamp

### Security Notice
Warning card about regularly reviewing active sessions

## Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Features in Detail

### Auto-Refresh
- Current time updates every second
- Session data refreshes every 30 seconds
- Relative times recalculate automatically

### Relative Time Display
The `getRelativeTime()` utility function converts timestamps to human-readable format:
- "just now" (less than 1 minute)
- "X minutes ago" (less than 1 hour)
- "X hours ago" (less than 24 hours)
- "X days ago" (24+ hours)

### Device Icons
- **Desktop**: Monitor icon
- **Mobile**: Smartphone icon
- **Tablet**: Tablet icon

### Status Badges
- **Active**: Green badge
- **Inactive**: Gray badge
- **Current**: Secondary badge on device name

## Mock Data

The frontend includes mock session data for development when the API is unavailable:
- MacBook Pro (desktop, current)
- iPhone 15 Pro (mobile)
- iPad Air (tablet)
- Windows Desktop (desktop, inactive)

## Styling

The application uses:
- **Tailwind CSS**: Utility-first styling
- **CSS Variables**: For theme customization
- **Dark Mode**: Support via `dark:` prefix
- **Responsive Design**: Mobile-first approach

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Requires JavaScript enabled

## Performance

- Server-side rendering with Next.js App Router
- Optimized component re-renders
- Efficient auto-refresh with intervals
- Minimal bundle size with tree-shaking

## Security Features

- Cannot logout current session from the UI
- Clear visual indication of current session
- Security notice about unfamiliar devices
- IP address tracking for session verification
