# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AGENTX is a personal AI assistant framework designed to be a "full-on JARVIS" with memory, reasoning, and multimodal capabilities. The project combines local LLMs (via Ollama), programmatic LLM interactions (DSPy), persistent memory (Mem0AI), and plugin architecture (FastMCP).

### Key Technologies

- **DSPy 3.1+** - Programmatic LLM framework with ReAct agents
- **Mem0AI 1.0+** - Long-term memory with episodic/semantic/procedural storage
- **Ollama** - Local LLM inference (models: gemma3:4b, llama3.2, llava)
- **Qdrant** - Vector database for semantic search
- **FastMCP 2.0** - MCP (Model Context Protocol) server framework for plugins
- **FastAPI** - Backend API framework
- **Next.js + Tailwind CSS** - Frontend PWA

## Development Commands

### Environment Setup

```bash
# Create/activate virtual environment
source .venv/bin/activate

# Install PyTorch with CUDA 13.0 support (REQUIRED ORDER)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Install core dependencies
uv pip install -r requirements-core.txt

# Start Ollama (required for LLM backend)
ollama serve

# Pull required models
ollama pull gemma3:4b  # Primary chat model
ollama pull llama3.2   # Alternative chat model
ollama pull llava:latest  # Vision model
```

### Code Quality

```bash
# Run linter (fixes issues automatically)
ruff check --fix

# Format code
ruff format

# Type checking (optional - uses pyrefly)
pyrefly check
```

### Testing

```bash
# Run tests (pytest)
pytest

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test file
pytest tests/test_service.py
```

### Running Prototypes

Each prototype (R000-R012) has its own backend/frontend:

```bash
# Example: R011 Personal Assistant
cd prototypes/R011_personal_assistant/backend

# Start backend
python main.py

# In another terminal, start frontend
cd ../frontend
npm run dev
```

## Architecture Overview

### Core + Plugin Pattern

```
┌─────────────────────────────────────┐
│         AGENTX Core System          │
│  (DSPy + Mem0AI + ColBERTv2 RAG)    │
└─────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
┌──────────┬──────────┬──────────┐
│  Memory  │  Plugins │ Frontend │
│ (Mem0AI) │ (FastMCP)│  (PWA)   │
└──────────┴──────────┴──────────┘
```

### Directory Structure

```
AgentX/
├── prototypes/           # Prototype applications (R000-R012)
│   ├── R000_template/    # Template for new prototypes
│   ├── R001-R010/        # Various feature prototypes
│   └── R011_personal_assistant/  # Personal Assistant (DSPy + Voice)
├── docs/research/        # Comprehensive research documentation
├── pyproject.toml        # UV package manager configuration
├── requirements-core.txt # Core dependencies (excluding PyTorch)
└── requirements-pytorch.txt  # PyTorch with CUDA 13.0
```

### Prototype Levels

Prototypes are organized by complexity levels:
- **Level 1-3**: Basic CRUD, state management, API integration
- **Level 4-5**: Real-time features (WebSocket), voice (STT/TTS)
- **Level 6**: AI assistants with DSPy ReAct + tools
- Each prototype builds on patterns from previous ones

## DSPy Integration Patterns

### Configuring DSPy with Ollama

DSPy has **built-in Ollama support** - no separate `ollama` package needed:

```python
import dspy

# Configure LM (language model)
lm = dspy.LM(
    "ollama_chat/gemma3:4b",  # Note: ollama_chat/ prefix
    api_base="http://localhost:11434",
    api_key=""  # Ollama doesn't require API key
)
dspy.configure(lm=lm)
```

### Creating ReAct Agents with Tools

```python
# Define tools as simple functions
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    result = eval(expression, {"__builtins__": {}}, {})
    return f"The result is: {result}"

# Create ReAct agent
react = dspy.ReAct(
    "question->answer",
    tools=[
        dspy.Tool(calculator, name="calculator"),
        dspy.Tool(search_function, name="search"),
    ]
)

# Use the agent
result = react(question="What is 123 * 456?")
print(result.answer)
```

### Streaming Responses

```python
# Wrap ReAct with streaming
stream_react = dspy.streamify(
    react,
    stream_listeners=[
        dspy.streaming.StreamListener(
            signature_field_name="next_thought",
            allow_reuse=True
        )
    ]
)

# Iterate through tokens
for chunk in stream_react(question="..."):
    print(chunk, end="")
```

## FastMCP Plugin Architecture

### Creating an MCP Server

```python
from fastmcp import FastMCP

mcp = FastMCP("plugin-name")

@mcp.tool
def my_tool(param: str) -> dict:
    """Tool description becomes docstring."""
    return {"result": f"Processed: {param}"}

if __name__ == "__main__":
    mcp.run(transport="http", port=8080)
```

### Server Composition

```python
# Main AGENTX server
agentx = FastMCP("agentx-main")

# Mount external plugin servers
agentx.mount_server("company-mis", company_mis_server)
agentx.mount_server("vision", vision_server)

agentx.run()
```

## Voice Integration (Silero)

The project uses Silero for both STT and TTS. Key requirements:

### Audio Pipeline Requirements

- **Input STT**: 24kHz → resample to 16kHz (Silero requirement)
- **Output TTS**: 16kHz sample rate
- **Format**: WAV files required for both

### STT Service Pattern

```python
import torch
import torchaudio

# Load Silero STT model
model, decoder, utils = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                       model='silero_stt',
                                       language='en',
                                       device='cuda' if torch.cuda.is_available() else 'cpu')

# Transcribe audio
def transcribe(audio_path: str) -> str:
    # Resample to 16kHz if needed
    waveform, sample_rate = torchaudio.load(audio_path)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)

    # Transcribe
    text = decoder(model(waveform[0].to(device))[0])
    return text
```

### TTS Service Pattern

```python
from silero import TextToSpeech

# Initialize TTS
tts = TextToSpeech(models_dir="models/")
tts.load_model(language='en', speaker='random')

# Generate speech
audio_path = tts.synthesize(text="Hello world", output_file="output.wav")
```

## FastAPI Backend Patterns

### Project Structure (per prototype)

```
backend/
├── main.py              # Application entry point
├── config/
│   └── settings.py      # Pydantic Settings
├── api/
│   └── routes.py        # FastAPI router
├── services/
│   ├── service.py       # Business logic
│   ├── stt_service.py   # Speech-to-Text
│   └── tts_service.py   # Text-to-Speech
└── models/
    └── schemas.py       # Pydantic models
```

### Settings Pattern

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "My App"
    version: str = "0.1.0"
    port: int = 8000
    debug: bool = True
    llm_model: str = "gemma3:4b"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

### WebSocket Voice Endpoint

```python
from fastapi import WebSocket

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            # Receive audio chunk
            audio_data = await websocket.receive_bytes()

            # STT → DSPy → TTS pipeline
            text = stt_service.transcribe(audio_data)
            response = await assistant_service.process_message(text)
            audio_output = tts_service.synthesize(response)

            # Send back audio
            await websocket.send_bytes(audio_output)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

## Frontend Patterns (Next.js + Tailwind)

### Tailwind Configuration

**CRITICAL**: Tailwind requires explicit configuration files or styling won't load:

```typescript
// tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
};
```

### shadcn/ui Color Variables

```css
/* app/globals.css */
:root {
  --border: 214.3 31.8% 91.4%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
}

.dark {
  --border: 217.2 32.6% 17.5%;
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
}
```

## Important Policy Rules

This project has a strict code enforcement policy (CLAUDE_POLICY.md):

1. **ABSOLUTE IMPORTS ONLY** - Never use `from .` or `from ..`
   - ✅ `from app.domain.mock.entities import MockDefinition`
   - ❌ `from .entities import MockDefinition`

2. **Ruff Compliance** - All code must pass:
   ```bash
   ruff check --fix
   ruff format
   ```

3. **File Size Limits** - Max 100 lines of executable code per file (50 lines overhead)

4. **No Anti-Patterns** - No god objects, magic numbers, circular imports, or "cleanup later" code

## External Service Dependencies

### Ollama (Required)
- **URL**: http://localhost:11434
- **Models**: gemma3:4b (recommended), llama3.2, llava:latest
- **Start**: `ollama serve`

### SearXNG (Optional - for web search)
- **URL**: http://192.168.1.4:8080 or http://localhost:8080
- **Purpose**: Privacy-focused metasearch engine

### Qdrant (Optional - for vector storage)
- **URL**: http://localhost:6333
- **Purpose**: Vector database for semantic search

## Common Issues & Solutions

### Issue: "No module named 'dspy'"
**Solution**: Install DSPy: `uv pip install dspy-ai`

### Issue: Tailwind CSS not loading (unstyled pages)
**Solution**: Ensure `tailwind.config.ts` and `postcss.config.js` exist in frontend root

### Issue: CUDA not available (PyTorch CPU only)
**Solution**: Install PyTorch with CUDA first:
```bash
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

### Issue: Ollama connection refused
**Solution**: Start Ollama: `ollama serve`

### Issue: DSPy Ollama backend not working
**Solution**: Use `ollama_chat/` prefix: `dspy.LM("ollama_chat/gemma3:4b", ...)`

## Research Documentation

Comprehensive research docs are available in `docs/research/`:
- `00_research_summary.md` - Architecture overview
- `02_dspy_mem0_integration.md` - DSPy + Mem0 patterns
- `11_fastmcp_guide.md` - Complete FastMCP reference

See `README.md` for full project documentation.
