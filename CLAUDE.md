# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: Read CLAUDE_POLICY.md First

**Before making any code changes, you MUST read and adhere to `CLAUDE_POLICY.md`.**

This policy is strictly enforced and includes:
- Absolute imports only (no `from .` or `from ..`)
- Ruff compliance (mandatory)
- Pyrefly type checking (mandatory)
- File size limits
- Anti-pattern prohibition

**Code that violates CLAUDE_POLICY.md is invalid and must be fixed before responding.**

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

# Type checking with pyrefly
pyrefly check --summarize-errors

# Run on all prototypes (from root)
for dir in prototypes/*/backend; do cd "$dir" && ruff check . && ruff format . && pyrefly check . --summarize-errors; done
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
├── prototypes/           # Prototype applications (R000-R013+) - IMPLEMENTATION REFERENCES
│   ├── R000_template/    # Template for new prototypes
│   ├── R001-R010/        # Various feature prototypes
│   ├── R011_personal_assistant/  # Personal Assistant (DSPy + Voice)
│   └── R013_travel_planning_stream/  # WebSocket streaming patterns
├── docs/
│   ├── engineering/      # HLD, LLD, schemas, threat model, privacy
│   └── research/         # Comprehensive research documentation
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

### Reference Hierarchy (Step-by-Step Research Method)

**When implementing new features, follow this logical reference order:**

| Step | Reference | Purpose | Location |
|------|-----------|---------|----------|
| **0** | **Research & Learnings** | Foundational knowledge, patterns | `docs/research/`, `docs/learnings/` |
| **1** | **Existing Prototypes** | Working implementation patterns | `prototypes/R000-R013/` |
| **2** | **Engineering Docs** | Architecture, schemas, security, UI design | `docs/engineering/` |
| **3** | **DSPy Tutorials** | Agent patterns, streaming, tools | `/home/riju279/Downloads/dspy-main/dspy-main/docs/` |
| **4** | **Mimicus Backend** | Clean Architecture patterns | `/home/riju279/Documents/Tools/mimicus/mimicus/src/` |

#### Step 0: Research Documents (`docs/research/`)

| Document | Purpose | Key Topics |
|----------|---------|------------|
| `00_research_summary.md` | Architecture overview | Core concepts, tech stack |
| `01_colbert_qdrant_guide.md` | Vector search integration | ColBERTv2, Qdrant setup |
| `02_dspy_mem0_integration.md` | DSPy + Mem0AI patterns | ReAct agents, memory system |
| `03_ollama_local_llm.md` | Local LLM setup | Ollama configuration |
| `04_plugin_architecture.md` | Plugin system design | FastMCP patterns |
| `05_mcp_integration.md` | MCP protocol | Model Context Protocol |
| `06_pwa_frontend.md` | Frontend architecture | Next.js, PWA patterns |
| `07_temporal_rag.md` | Time-aware RAG | Fact invalidation, TTL |
| `08_tts_stt_integration.md` | Voice interface | STT/TTS pipeline |
| `09_computer_vision.md` | Vision capabilities | Multi-modal processing |
| `10_generative_ui_ollama_models.md` | Generative UI research | UI generation with LLMs |
| `11_fastmcp_guide.md` | FastMCP reference | Complete guide |
| `12_ovos_architecture_analysis.md` | OVOS pattern analysis | Voice assistant architecture |
| `13_blender_plugin_architecture_analysis.md` | Blender plugin patterns | Plugin design principles |
| `14_core_vs_plugin_separation_principles.md` | Core/plugin boundaries | Architecture separation |
| `15_comprehensive_research_summary.md` | All research summary | Consolidated findings |

#### Step 0: Learning Documents (`docs/learnings/`)

| Document | Purpose | Key Topics |
|----------|---------|------------|
| `00-overall-patterns-and-lessons.md` | Cross-pattern synthesis | All levels combined |
| `01-level-1-2-basics-crud-websocket-time-series.md` | Basic patterns | CRUD, WebSocket, time-series |
| `02-level-3-authentication-sessions-encryption.md` | Auth & security | Sessions, encryption |
| `03-level-4-documents-ai-vector-search.md` | Document + AI | Vector search patterns |
| `04-level-5-voice-stt-tts-vad.md` | Voice pipeline | STT/TTS/VAD integration |
| `05-level-6-ai-assistant-analytics.md` | AI assistant patterns | ReAct, analytics |

#### Step 2: Engineering Documents (`docs/engineering/`)

| Document | Purpose | Key Topics |
|----------|---------|------------|
| `generative_ui_design_plan.md` | Generative UI design plan | DSPy+LangGraph architecture, UI descriptors, fallback strategy |
| `HLD.md` | High-level design | System architecture, component catalog |
| `schemas.md` | Data schemas | Pydantic models, CanonicalDocument, plugin manifests |
| `threat_model.md` | Security threat model | STRIDE analysis, mitigation strategies |
| `privacy_assessment.md` | Privacy impact assessment | PII handling, GDPR/CCPA compliance |
| `openapi.yaml` | API specification | REST endpoints, WebSocket, data models |

#### Example Research Process for UI Agent:

**Foundational (Step 0)**:
1. Read `docs/research/10_generative_ui_ollama_models.md` for generative UI concepts
2. Read `docs/learnings/05-level-6-ai-assistant-analytics.md` for AI assistant patterns
3. Read `docs/research/02_dspy_mem0_integration.md` for DSPy integration

**Implementation (Steps 1-4)**:
4. Check `R011_personal_assistant` for DSPy ReAct patterns
5. Check `R013_travel_planning_stream` for WebSocket streaming
6. Read `docs/engineering/generative_ui_design_plan.md` for UI architecture
7. Read `docs/engineering/schemas.md` for data structure standards
8. Read DSPy `tutorials/streaming/` for `dspy.streamify()` patterns
9. Read mimicus `domain/entities/` for Clean Architecture entity patterns

### Package Management

**Always use `uv` for package management**:

```bash
# Add new packages
uv add package-name

# Add with extras
uv add "package-name[extra]"

# Add dev dependency
uv add --dev package-name

# Install from requirements
uv pip install -r requirements-core.txt

# Install PyTorch with CUDA (special index URL)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Sync lockfile
uv sync
```

### Backend Architecture Standards (from Mimicus)

**IMPORTANT**: Follow **Clean Architecture / Domain-Driven Design (DDD)** patterns for all new backend code:

```
prototype_name/backend/
├── main.py              # Application entry point (FastAPI factory)
├── core/                # Configuration & dependency injection
│   ├── config.py        # Pydantic Settings
│   ├── dependencies.py  # Dependency injection functions (singletons)
│   └── middleware/      # CORS, logging, auth middleware
├── domain/              # Innermost layer - business logic (no dependencies)
│   ├── entities/        # Core business entities (@dataclass)
│   ├── repositories/    # Repository interfaces (ABC) + implementations
│   └── services/        # Domain services (business logic)
├── application/         # Use cases orchestration
│   ├── use_cases/       # Single-purpose classes with execute()
│   ├── dtos/            # Data Transfer Objects (Pydantic models for API)
│   └── mappers/         # Entity ↔ DTO conversion (static methods)
├── infrastructure/      # External concerns (DB, HTTP, storage)
│   ├── database/        # SQLAlchemy models, connection
│   └── external/        # HTTP clients, external APIs
└── presentation/        # FastAPI routes (controllers)
    └── api/
        └── v1/          # REST endpoints
```

**Key Patterns** (see mimicus `/home/riju279/Documents/Tools/mimicus/mimicus/src/`):

1. **Repository Pattern**: Abstract base class + implementations
2. **DTO Pattern**: Pydantic models for API layer (CreateDTO, ResponseDTO)
3. **Mapper Pattern**: Static methods for entity ↔ DTO conversion
4. **Use Case Pattern**: Single-purpose classes with `execute()` method
5. **Dependency Injection**: Global singletons + getter functions
6. **Entity Pattern**: `@dataclass` with business logic methods

**Variable Naming Conventions**:
- Entity properties: `mock_id`, `mock_name`, `mock_enabled`
- Match criteria: `match_method`, `match_path`, `match_headers`
- Response config: `response_status`, `response_body`
- Repository instances: `_mock_repository`, `_user_repository`
- Use case functions: `get_create_mock_use_case()`

**File Size Constraints**: Max 100 lines of executable code per file (50 lines overhead).

### DSPy Documentation Reference

**IMPORTANT**: DSPy tutorials are available at `/home/riju279/Downloads/dspy-main/dspy-main/docs/`

**Key Tutorials** (always combine 3+ examples for complex problems):
- `docs/tutorials/streaming/index.md` - Token/status streaming with `dspy.streamify()`
- `docs/tutorials/async/index.md` - Async patterns with `acall()`, `aforward()`
- `docs/tutorials/tool_use/index.ipynb` - Tool use patterns
- `docs/tutorials/agents/index.ipynb` - ReAct agent optimization
- `docs/tutorials/mem0_react_agent/index.md` - Memory-enabled agents
- `docs/tutorials/yahoo_finance_react/index.md` - Real-world ReAct integration
- `docs/learn/programming/tools.md` - Complete tools reference
- `docs/learn/programming/signatures.md` - DSPy signatures

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

- **Input STT**: Any sample rate → resample to 16kHz (Silero STT requirement)
- **Output TTS**: 24kHz or 48kHz sample rate (Silero TTS output)
- **Format**: WAV files required for both
- **VAD**: 16kHz sample rate required for voice activity detection

### STT Service Pattern

```python
import torch
import numpy as np
import scipy.io.wavfile as wavfile

# Load Silero STT model
stt_result = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_stt',
    language='en',
    device=self._torch_device,
    trust_repo=True,
)

self.stt_model = stt_result[0]  # type: ignore[index]
self.stt_decoder = stt_result[1]  # type: ignore[index]
utils_tuple = stt_result[2]  # type: ignore[index]
self._stt_read_batch = utils_tuple[0]  # type: ignore[index]
self._stt_prepare_model_input = utils_tuple[3]  # type: ignore[index]

# Transcribe audio (accepts any sample rate)
STT_SAMPLE_RATE = 16000

async def transcribe(self, audio_bytes: bytes) -> str:
    # Save to temp file
    temp_path = f"/tmp/temp_stt_{uuid.uuid4().hex}.wav"
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)

    # Read and validate
    sr, audio_data = wavfile.read(temp_path)

    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = audio_data.mean(axis=1)

    # Resample if not 16kHz
    if sr != self.STT_SAMPLE_RATE:
        # Use torchaudio or scipy for resampling
        from torchaudio.transforms import Resample
        audio_tensor = torch.from_numpy(audio_data.astype(np.float32) / 32768.0)
        if audio_tensor.dim() == 1:
            audio_tensor = audio_tensor.unsqueeze(0)
        resampler = Resample(sr, self.STT_SAMPLE_RATE)
        audio_tensor = resampler(audio_tensor)
        audio_data = audio_tensor.squeeze().numpy()
        sr = self.STT_SAMPLE_RATE

    # Prepare and transcribe
    input_batch = self._stt_prepare_model_input(
        self._stt_read_batch([temp_path]), device=self._torch_device
    )
    with torch.no_grad():
        output = self.stt_model(input_batch)
    text = self.stt_decoder(output[0].cpu())
    return text
```

### TTS Service Pattern

```python
from silero import silero_tts

# Initialize TTS (variable-length return)
tts_result = silero_tts(language="en", speaker="v3_en")
if isinstance(tts_result, tuple) and len(tts_result) >= 2:
    self.tts_model = tts_result[0]
    self.tts_example_text = tts_result[1]
else:
    self.tts_model = tts_result
    self.tts_example_text = "Hello world"

if hasattr(self.tts_model, "to"):
    self.tts_model.to(self._torch_device)

# Generate speech (24kHz or 48kHz output)
TTS_SAMPLE_RATE = 24000  # or 48000

async def synthesize(self, text: str) -> bytes:
    # Generate audio at exact sample rate
    audio = self.tts_model.apply_tts(
        text=text, speaker="en_5", sample_rate=self.TTS_SAMPLE_RATE
    )

    # Save to WAV
    import io
    import scipy.io.wavfile as wavfile

    audio_buffer = io.BytesIO()
    wavfile.write(audio_buffer, self.TTS_SAMPLE_RATE, audio.cpu().numpy())
    audio_buffer.seek(0)
    return audio_buffer.read()
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

**CRITICAL**: This project has a strict code enforcement policy defined in `CLAUDE_POLICY.md`.

You **MUST** read and adhere to `CLAUDE_POLICY.md` when writing or modifying code. Key requirements:

1. **ABSOLUTE IMPORTS ONLY** - Never use `from .` or `from ..`
   - ✅ `from config.settings import settings`
   - ❌ `from .settings import settings`

2. **Ruff Compliance** - All code must pass:
   ```bash
   ruff check --fix
   ruff format
   ```

3. **Pyrefly Type Checking** - All code must pass:
   ```bash
   pyrefly check --summarize-errors
   ```

4. **File Size Limits** - Max 100 lines of executable code per file (50 lines overhead)

5. **No Anti-Patterns** - No god objects, magic numbers, circular imports, or "cleanup later" code

6. **Self-Correction Required** - If any check fails, you must fix the code before responding

### Quality Loop Process

When making code changes, follow this loop:

```bash
# 1. Make your changes
# 2. Run ruff check
ruff check . --fix

# 3. Run ruff format
ruff format .

# 4. Run pyrefly check
pyrefly check . --summarize-errors

# 5. If any errors remain, fix them and repeat from step 2
```

**Do not consider code changes complete until all checks pass.**

## Type Checking Patterns (Pyrefly)

Pyrefly is used for strict type checking. Common patterns to satisfy pyrefly:

### PyTorch Device Attribute Pattern

PyTorch's `torch.device` is a read-only descriptor. Use this pattern to avoid pyrefly errors:

```python
class MyService:
    def __init__(self):
        use_cuda = torch.cuda.is_available()
        device_str = "cuda" if use_cuda else "cpu"
        self._torch_device = torch.device(device_str)  # type: ignore[read-only]
        if use_cuda:
            logger.info(f"Using GPU: {torch.cuda.get_device_name()}")
        else:
            logger.info("Using CPU")
```

**Key points:**
- Rename `self.device` to `self._torch_device`
- Use `use_cuda` variable before assignment
- Add `# type: ignore[read-only]` comment
- Use `self._torch_device` in all subsequent references

### torch.hub.load Indexing Pattern

torch.hub.load returns `object` type. Add type ignore comments:

```python
stt_result = torch.hub.load(
    repo_or_dir="snakers4/silero-models",
    model="silero_stt",
    language="en",
    device=self._torch_device,
    trust_repo=True,
)

self.stt_model = stt_result[0]  # type: ignore[index]
self.stt_decoder = stt_result[1]  # type: ignore[index]
utils_tuple = stt_result[2]  # type: ignore[index]
self._stt_read_batch = utils_tuple[0]  # type: ignore[index]
self._stt_prepare_model_input = utils_tuple[3]  # type: ignore[index]
```

### silero_tts Unpacking Pattern

silero_tts has variable-length return values:

```python
from silero import silero_tts

tts_result = silero_tts(language="en", speaker="v3_en")
# Handle variable-length return from silero_tts
if isinstance(tts_result, tuple) and len(tts_result) >= 2:
    self.tts_model = tts_result[0]
    self.tts_example_text = tts_result[1]
else:
    self.tts_model = tts_result
    self.tts_example_text = "Hello world"  # Default example text
# Ensure the model is on the correct device
if hasattr(self.tts_model, "to"):
    self.tts_model.to(self._torch_device)
```

### VAD Model sr Argument

VAD model requires explicit sample rate argument:

```python
from silero_vad import VADIterator, load_silero_vad

vad_model = load_silero_vad()
# Always include sr parameter
speech_prob = vad_model(
    torch.tensor(audio_np).float().to(self._torch_device), sr=16000
).item()
```

### Forward References with Enum

When using Enum types before they're defined, add future import:

```python
from __future__ import annotations

from enum import Enum
from pydantic import BaseModel

class Document(BaseModel):
    status: DocumentStatus  # Forward reference works now

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
```

### MCP Import Pattern

MCP imports are dynamically generated and not recognized by type checkers:

```python
from mcp__tavily__tavily_search import tavily_search as mcp_tavily  # type: ignore[import]
```

### DSPy ReAct Signature Pattern

DSPy ReAct signature may trigger type errors:

```python
self.react = dspy.ReAct(
    "question->answer",  # type: ignore[arg-type]
    tools=[
        dspy.Tool(calculator, name="calculator"),
    ]
)
```

### Internal vs API Schemas

Keep internal data classes separate from API response schemas:

```python
# Internal storage (not exposed via API)
class Document(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    status: DocumentStatus
    extracted_text: str = ""

# API response schema
class DocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    status: DocumentStatus
```

Import only what you need in each layer:
- `services/service.py`: Import internal classes (`Document`, `Summary`)
- `api/routes.py`: Import response schemas (`DocumentResponse`, `SummaryResponse`)

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
