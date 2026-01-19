# AGENTX R014: Generative UI Showcase

**Level**: Frontend-Focused (Weak Backend, Strong Frontend)
**Status**: In Development
**Tech Stack**: FastAPI + Next.js 15 + shadcn/ui + Framer Motion

---

## Overview

R014 is a **UI showcase prototype** that demonstrates the complete generative UI system for AGENTX. Unlike other prototypes that focus on backend agent logic, R014 focuses on **frontend visual design** with mock data.

### Key Features

- ✅ **7 Generative UI Widgets**: Text/Markdown, Card, Form, Progress, Action, Confirmation, Voice
- ✅ **Full Animation System**: Fade, slide, scale, bounce transitions with Framer Motion
- ✅ **Dark/Light Mode**: Complete theme switching with shadcn/ui
- ✅ **Interactive Demos**: Try each widget with sample data
- ✅ **Widget Gallery**: View all components in isolation
- ✅ **Background Animation**: Subtle particle/wave effect
- ✅ **Responsive Design**: Mobile and desktop layouts

### What's Different from Other Prototypes

| Aspect | Other Prototypes | R014 |
|--------|-----------------|------|
| **Backend** | DSPy agents, LangGraph, LLMs | Mock data only |
| **Focus** | Agent behavior, tools, memory | UI design, animations, UX |
| **Complexity** | High (agent logic) | Low (static data) |
| **Purpose** | Test AI capabilities | Demo UI/UX design |

---

## Quick Start

### Backend (Mock Data API)

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Run mock server
python main.py
```

Backend runs on `http://localhost:8014`

### Frontend (UI Showcase)

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs on `http://localhost:3014`

---

## Project Structure

```
R014_ui_showcase/
├── backend/                    # FastAPI (Mock Data Only)
│   ├── api/
│   │   └── routes.py          # Mock UI descriptor endpoints
│   ├── data/
│   │   └── mock_descriptors.py # Pre-built UI examples
│   └── main.py
│
├── frontend/                   # Next.js (Full UI Showcase)
│   ├── app/
│   │   ├── page.tsx           # Main showcase page
│   │   ├── gallery/
│   │   │   └── page.tsx       # Widget gallery
│   │   └── layout.tsx         # Dark mode toggle
│   ├── components/
│   │   ├── showcase/          # Showcase-specific components
│   │   │   ├── widget-display.tsx
│   │   │   ├── background-animation.tsx
│   │   │   └── theme-toggle.tsx
│   │   └── widgets/           # All 7 generative UI widgets
│   │       ├── markdown-widget.tsx
│   │       ├── card-widget.tsx
│   │       ├── form-widget.tsx
│   │       ├── progress-widget.tsx
│   │       ├── action-widget.tsx
│   │       ├── confirmation-widget.tsx
│   │       └── voice-widget.tsx
│   └── lib/
│       └── mock-data.ts       # Client-side mock data
│
├── README.md
├── PRD.md
└── REPORTCARD.md
```

---

## Widget Gallery

### 1. Markdown Block
- **Purpose**: Display text and formatted content
- **Animation**: Fade in (200ms)
- **Variants**: Plain text, Markdown with syntax highlighting

### 2. Card
- **Purpose**: Display structured information with actions
- **Animation**: Slide up + fade (300ms)
- **Variants**: Search results, weather, data cards

### 3. Form
- **Purpose**: Collect user input with multiple fields
- **Animation**: Scale in (250ms)
- **Variants**: Login, survey, data entry

### 4. Progress
- **Purpose**: Show task completion status
- **Animation**: Expand (200ms)
- **Variants**: Determinate, indeterminate, striped

### 5. Action
- **Purpose**: Single-button interaction
- **Animation**: Bounce on hover (150ms)
- **Variants**: Primary, destructive, outline

### 6. Confirmation
- **Purpose**: Yes/No dialog for critical actions
- **Animation**: Scale + fade (200ms)
- **Variants**: Default, destructive (red)

### 7. Voice
- **Purpose**: Voice recording with waveform
- **Animation**: Pulse recording
- **Variants**: Idle, listening, processing, speaking

---

## Design System

### Colors (shadcn/ui)

```css
/* Light mode */
--primary: 222.2 47.4% 11.2%        /* Dark blue-gray */
--background: 0 0% 100%             /* White */
--foreground: 222.2 84% 5%          /* Near black */

/* Dark mode */
--background: 222.2 84% 5%          /* Very dark blue-gray */
--foreground: 210 40% 98%           /* Near white */
```

### Typography

- **Font**: Inter (system-ui fallback)
- **Scale**: xs (12px) → 3xl (30px)
- **Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Animations

| Type | Duration | Easing |
|------|----------|--------|
| Fade | 200ms | easeInOut |
| Slide | 300ms | easeOut |
| Scale | 250ms | easeOutBack |
| Bounce | 150ms | easeOutBounce |

---

## API Endpoints

### GET /api/v1/mock/descriptors
Returns all mock UI descriptors

```json
[
  {
    "id": "markdown-1",
    "type": "markdown",
    "content": "## Welcome to AGENTX\n\nThis is a **generative UI** demo."
  },
  {
    "id": "card-1",
    "type": "card",
    "title": "Search Results",
    "content": "Found 3 results",
    "actions": [...]
  }
]
```

### GET /api/v1/mock/descriptors/{type}
Returns descriptors of specific type

### GET /api/v1/mock/stream
Server-sent events stream (simulates agent streaming)

---

## Development Scripts

### Backend
```bash
./scripts/run.sh    # Start server
./scripts/test.sh   # Run tests
./scripts/lint.sh   # Run ruff
```

### Frontend
```bash
npm run dev     # Start dev server
npm run build   # Build for production
npm run lint    # Run ESLint
```

---

## Testing the UI

### 1. View Widget Gallery
Visit `http://localhost:3014/gallery` to see all widgets in isolation

### 2. Try Interactive Demo
Visit `http://localhost:3014` for the main showcase with live demos

### 3. Test Dark Mode
Click the theme toggle in the top-right corner

### 4. Test Animations
Hover over buttons, click forms, watch transitions

---

## Known Limitations (By Design)

- ❌ **No real LLM**: All responses are pre-written mock data
- ❌ **No DSPy agents**: No tool use, no ReAct loops
- ❌ **No memory**: No Qdrant, no Mem0AI, no vector search
- ❌ **No WebSocket**: Simulated streaming with SSE
- ❌ **No voice**: Voice widget is visual only (no STT/TTS)

---

## Future Enhancements

- [ ] Connect to real backend (R011 or R013)
- [ ] Add more widget variants
- [ ] Implement real voice recording
- [ ] Add widget state persistence
- [ ] Create widget playground (drag-and-drop)

---

## Related Prototypes

- **R011**: Personal Assistant with real DSPy agents
- **R013**: Travel Planning with WebSocket streaming
- **Phase 2-5 Tasks**: Backend agent implementation

---

**Part of AGENTX Prototypes Program**
