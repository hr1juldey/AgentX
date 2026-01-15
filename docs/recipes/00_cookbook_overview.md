# AGENTX Prototype Cookbook

**A progressive learning journey from basic CRUD to AI-powered applications.**

## Overview

This cookbook contains 12 full-stack prototypes that teach you how to build production-ready applications using FastAPI (backend) and Next.js + shadcn/ui (frontend). Each prototype is a complete, working application with real user utility.

## Philosophy

1. **Full-Stack Each**: Every prototype has both backend and frontend
2. **1-2 Hours**: Can be built in a single sitting
3. **Real Utility**: Every app is something you'll actually use
4. **Rising Difficulty**: Learn gradually, from simple to complex
5. **Production Patterns**: These patterns apply directly to AGENTX

## The Journey: 6 Levels

```
Level 1 (Basic CRUD)    →  Learn: FastAPI routes, SQLite, Next.js pages
     ↓
Level 2 (Background)    →  Learn: WebSocket, real-time updates, charts
     ↓
Level 3 (Authentication) →  Learn: JWT, encryption, Redis sessions
     ↓
Level 4 (Documents & AI) →  Learn: File upload, LLM streaming, vector search
     ↓
Level 5 (Voice)         →  Learn: TTS/STT, VAD, audio streaming
     ↓
Level 6 (AI Assistant)  →  Learn: DSPy ReAct, tool calling, analytics
```

## Recipe Menu

### Level 1: Basic CRUD (1-1.5 hours each)

#### R001: Personal Notes
- **Utility**: Quick note-taking app
- **Backend**: SQLite CRUD with 3 endpoints
- **Frontend**: Note list + editor modal
- **Components**: Card, Button, Input, Textarea, Dialog
- **Learn**: FastAPI basics, Next.js App Router, shadcn/ui setup

#### R002: Todo List
- **Utility**: Task management with due dates
- **Backend**: 4 endpoints + date filtering
- **Frontend**: Kanban board (3 columns) + calendar toggle
- **Components**: Card, Badge, Calendar, Select
- **Learn**: Advanced CRUD, date handling, drag-drop UI

---

### Level 2: Background Tasks (1.5 hours each)

#### R003: Pomodoro Timer
- **Utility**: Productivity timer with sessions
- **Backend**: WebSocket countdown + session history
- **Frontend**: Timer display + session stats
- **Components**: Progress, Button, Card
- **Learn**: WebSocket real-time communication

#### R004: Habit Tracker
- **Utility**: Daily habit tracking with streaks
- **Backend**: Time-series aggregation + streak calculation
- **Frontend**: Habit list + streak counter + line chart
- **Components**: Card, Checkbox, Progress, Recharts
- **Learn**: Data aggregation, charting, streak logic

---

### Level 3: Authentication (2 hours each)

#### R005: Password Manager
- **Utility**: Secure credential vault
- **Backend**: Encryption + JWT auth + CRUD
- **Frontend**: Vault grid + password generator modal
- **Components**: Card, Input, Button, Dialog, Table
- **Learn**: Password hashing, JWT tokens, encryption

#### R006: Session Manager
- **Utility**: Multi-device login management
- **Backend**: Redis sessions + device tracking
- **Frontend**: Login page + active sessions table
- **Components**: Form, Input, Button, Table, Badge
- **Learn**: Redis integration, session management

---

### Level 4: Documents & AI (2 hours each)

#### R007: PDF Summarizer
- **Utility**: Summarize PDF documents with AI
- **Backend**: PDF upload + LLM streaming
- **Frontend**: Dropzone upload + summary display
- **Components**: Card, Button, Progress, ScrollArea
- **Learn**: File upload, PDF parsing, LLM integration

#### R008: Smart Search
- **Utility**: Semantic file search
- **Backend**: Qdrant + FastEmbed embeddings
- **Frontend**: Search bar + results grid
- **Components**: Input, Card, Badge, Skeleton
- **Learn**: Vector databases, embeddings, semantic search

---

### Level 5: Voice Interface (2 hours each)

#### R009: Voice Memos
- **Utility**: Record voice notes with transcription
- **Backend**: STT + TTS + file storage
- **Frontend**: Recorder + transcription display
- **Components**: Card, Button, Mic (custom), ScrollArea
- **Learn**: Audio recording, speech-to-text, text-to-speech

#### R010: Meeting Notes
- **Utility**: Real-time meeting transcription
- **Backend**: VAD + streaming STT + timestamps
- **Frontend**: Real-time captions + speaker labels
- **Components**: Card, Badge, ScrollArea, Progress
- **Learn**: Voice Activity Detection, streaming STT

---

### Level 6: AI Assistant (2 hours each)

#### R011: Personal Assistant
- **Utility**: JARVIS-like helper with tools
- **Backend**: DSPy ReAct + tool calling
- **Frontend**: Chat interface + tool status panel
- **Components**: Card, Input, Button, ScrollArea, Badge
- **Learn**: AI agents, ReAct prompting, tool use

#### R012: Analytics Dashboard
- **Utility**: Personal metrics dashboard
- **Backend**: Aggregation endpoints
- **Frontend**: Dashboard + date range + charts
- **Components**: Card, DatePicker, LineChart, BarChart
- **Learn**: Data aggregation, complex dashboards

---

## How to Use This Cookbook

### For Each Prototype:

1. **Copy the template**:
   ```bash
   cp -r prototypes/R000_template prototypes/RXXX_prototype_name
   ```

2. **Read the PRD**: Check what you're building

3. **Build the backend**:
   - Update `.env` with app name
   - Create API routes in `api/routes.py`
   - Run `./scripts/run.sh`

4. **Build the frontend**:
   - Update `.env.local` with API URL
   - Create pages in `app/`
   - Run `./scripts/dev.sh`

5. **Test and document**:
   - Run `./scripts/test.sh` (backend)
   - Run `./scripts/lint.sh` (frontend)
   - Fill out REPORTCARD.md

---

## Template Structure

```
prototypes/R000_template/          # Master template
│
├── backend/                        # FastAPI Backend
│   ├── config/settings.py          # Pydantic Settings
│   ├── models/schemas.py           # Request/response models
│   ├── services/                   # Business logic
│   ├── api/routes.py               # FastAPI routes
│   ├── tests/                      # Pytest tests
│   └── scripts/                    # run.sh, test.sh, lint.sh
│
├── frontend/                       # Next.js Frontend
│   ├── app/                        # Next.js App Router
│   ├── components/ui/              # shadcn/ui components
│   └── scripts/                    # dev.sh, build.sh, lint.sh
│
├── README.md                       # Usage instructions
├── PRD.md                          # Product requirements
└── REPORTCARD.md                   # Lessons learned
```

---

## Subagent Development Strategy

To build prototypes faster (~40% time savings):

### Parallel Building (Level 1-2):
```
├─ Backend Builder ─────────────┐
│                              ├─→ Integration
└─ Frontend Builder ────────────┘
      ↓
├─ Backend Tests ──────────────┐
│                              ├─→ Reportcard
└─ Frontend Tests ─────────────┘
```

### Sequential Building (Level 3-4):
```
Backend → Frontend → Integration → Tests → Reportcard
```

### Component Parallel (Level 5-6):
```
├─ WebSocket Agent
├─ API Routes Agent
├─ Frontend Components ───→ Integration → Reportcard
└─ STT/TTS Integration
```

---

## Difficulty Progression

| Level | Recipes | Time/Recipe | New Concepts |
|-------|---------|-------------|--------------|
| 1 | R001-R002 | 1-1.5h | CRUD, SQLite, Next.js basics |
| 2 | R003-R004 | 1.5h | WebSocket, real-time, charts |
| 3 | R005-R006 | 2h | Auth, JWT, encryption, Redis |
| 4 | R007-R008 | 2h | File upload, LLM, vector search |
| 5 | R009-R010 | 2h | TTS/STT, VAD, audio streaming |
| 6 | R011-R012 | 2h | AI agents, analytics, dashboards |

**Total Time**: ~20 hours (sequential), ~11 hours (with subagents)

---

## Dependencies

### Backend (per prototype)
```
fastapi>=0.115.0
sqlmodel>=0.0.22
uvicorn[standard]>=0.30.0
pydantic>=2.9.0
pydantic-settings>=2.5.0
httpx>=0.27.0
python-dotenv>=1.0.0
```

Plus level-specific:
- Level 3: `fastapi-users`, `redis`
- Level 4: `pdfplumber`, `qdrant-client`, `fastembed`
- Level 5: `pocket-tts`, `silero-vad`
- Level 6: `dspy`, `pandas`

### Frontend (all prototypes)
```
next@^15.1.0
react@^19.0.0
react-dom@^19.0.0
tailwindcss@^3.4.0
@radix-ui/react-slot@^1.1.0
class-variance-authority@^0.7.0
tailwind-merge@^2.5.0
lucide-react@^0.468.0
```

Plus level-specific:
- Level 2: `recharts`
- Level 3: `@radix-ui/react-form`, `@radix-ui/react-select`
- Level 4: `react-dropzone`
- Level 6: `date-fns`, `recharts`

---

## Verification Checklist

Each prototype must pass:

- [ ] Backend tests: `pytest --cov` (≥80% coverage)
- [ ] Frontend lint: `eslint` (no errors)
- [ ] TypeScript: `tsc --noEmit` (no errors)
- [ ] Manual test: Both servers running, UI works
- [ ] Performance: API p95 <500ms, page load <2s
- [ ] REPORTCARD.md: Complete with metrics

---

## Next Steps

1. ✅ Use **R000_template** as starting point
2. ✅ Read the **recipe docs** for each level
3. ✅ Build prototypes in order (R001 → R012)
4. ✅ Fill out **REPORTCARD.md** after each
5. ✅ Apply learnings to **main AGENTX system**

---

## Resources

- **Template**: `prototypes/R000_template/`
- **Plan**: `/home/riju279/.claude/plans/resilient-nibbling-feigenbaum.md`
- **Dependencies**: `requirements-core.txt`, `requirements-pytorch.txt`
- **Installation**: `INSTALL.md`

---

**Start with R001: Personal Notes** and work your way through all 12 prototypes!

Each prototype teaches patterns you'll use in the main AGENTX system. Take notes, experiment, and have fun building!
