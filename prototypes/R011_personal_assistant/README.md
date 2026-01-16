# R011: Personal Assistant (Level 6)

AI-powered personal assistant with ReAct agent pattern.

## Features

- **ReAct Agent**: Reasoning + Acting pattern for tool use
- **Multi-Tool Support**: Calculator, Search, Weather tools
- **Conversation Memory**: Maintains conversation context
- **Structured Reasoning**: Thought, Action, Observation pattern

## Tech Stack

- **Backend**: FastAPI + Custom ReAct implementation
- **Frontend**: Next.js + shadcn/ui
- **Port**: 8011

## Quick Start

### Backend
```bash
cd backend
pip install -e .
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Tools Available

1. **Calculator**: Basic math operations
2. **Search**: Information lookup (mock)
3. **Weather**: Weather queries (mock)

## Notes

- Prototype uses simplified ReAct pattern
- Tools are mock implementations (connect real APIs for production)
- Conversation memory is in-memory only
- No actual LLM integration (responses are rule-based for prototype)
