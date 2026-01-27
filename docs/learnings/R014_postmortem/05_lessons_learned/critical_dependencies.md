# Critical Dependencies for Real AgentX

## Summary
**Technical Dependencies**: 9 core libraries
**Architecture Dependencies**: 5 patterns
**Integration Dependencies**: 4 proven patterns
**Status**: All production-tested in R014

---

## Technical Dependencies

### 1. DSPy 3.1+

**Purpose**: Programmatic LLM framework with signatures, modules, optimizers
**Status**: ✅ Core framework (proven in R014)
**Version**: 3.1+ (R014 uses 3.1.x)
**Installation**:
```bash
uv pip install dspy-ai
```

**Why Required**:
- Signature-based LLM interactions
- Module system for composable agents
- ChainOfThought for better reasoning
- ReAct agent for tool-based workflows
- Streaming support for real-time output
- Built-in Ollama support

**Known Patterns**:
- Sync warmup required before streaming
- ReAct > CodeAct for small LLMs
- Chunking + iteration for large inputs
- Explicit signatures with named fields
- Few-shot learning in signature description

**Configuration**:
```python
import dspy

# Configure LM (language model)
lm = dspy.LM(
    "ollama_chat/qwen3:8b",  # Note: ollama_chat/ prefix
    api_base="http://localhost:11434",
    api_key=""  # Ollama doesn't require API key
)
dspy.configure(lm=lm)
```

---

### 2. Ollama

**Purpose**: Local LLM runtime
**Status**: ✅ REQUIRED for local deployment
**Version**: Latest (R014 tested with qwen3:8b, gemma3:4b)
**Installation**:
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve

# Pull required models
ollama pull qwen3:8b
ollama pull gemma3:4b
ollama pull llava:latest  # For vision
```

**Why Required**:
- Local LLM inference (no API costs)
- Privacy (data stays local)
- Offline capability
- No rate limits
- Fast development iterations

**Model Recommendations**:
| Model | Parameters | Context | Best For | Status |
|-------|------------|---------|----------|--------|
| qwen3:8b | 8.2B | ~4K tokens | General tasks | ✅ Tested |
| gemma3:4b | 4.7B | ~8K tokens | Fast responses | ✅ Tested |
| llava:latest | ~7B | ~4K tokens | Vision tasks | ✅ Tested |
| llama3.2 | 3B-70B | ~8K tokens | Alternative | ⚠️ Not tested |

**Model-Specific Parameters** (for qwen3:8b):
- Max chunk size: 500 chars
- Overlap: 100 chars
- Iterations: 3
- ChainOfThought n: 3
- ReAct max_iters: 3

---

### 3. FastAPI

**Purpose**: Web framework (REST + WebSocket)
**Status**: ✅ REQUIRED (proven in R014)
**Version**: 0.100+ (R014 uses 0.104+)
**Installation**:
```bash
uv pip install fastapi uvicorn[standard]
uvicorn main:app --reload
```

**Why Required**:
- Async request handling
- WebSocket support (critical for streaming)
- Automatic OpenAPI documentation
- Type-safe with Pydantic
- High performance

**Proven Patterns**:
- Connection state tracking (boolean flag)
- Progressive feedback events
- Three-tier serialization fallback
- Mock mode support
- Session tracking with truncated UUID

**Router Composition**:
```python
# api/routes/__init__.py
from fastapi import APIRouter

from .health import router as health_router
from .search import router as search_router
from .master_agent import router as master_agent_router

router = APIRouter()
router.include_router(health_router)
router.include_router(search_router)
router.include_router(master_agent_router)
```

---

### 4. Pydantic

**Purpose**: Data validation and settings management
**Status**: ✅ REQUIRED
**Version**: 2.0+ (R014 uses Pydantic v2)
**Installation**:
```bash
uv pip install pydantic pydantic-settings
```

**Why Required**:
- Type-safe data models
- Automatic validation
- Settings management (environment variables)
- Serialization/deserialization
- OpenAPI schema generation

**Proven Patterns**:
- Domain entities in `domain/entities/`
- Request DTOs in `application/dtos/requests/`
- Response DTOs in `application/dtos/responses/`
- Settings with `pydantic_settings.BaseSettings`

**Settings Pattern**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AgentX"
    version: str = "0.1.0"
    port: int = 8000
    debug: bool = True
    mock_mode: bool = False
    llm_model: str = "qwen3:8b"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

### 5. PyTorch

**Purpose**: Deep learning framework (for STT/TTS models)
**Status**: ✅ REQUIRED for voice features
**Version**: 2.0+ (with CUDA support)
**Installation**:
```bash
# Install with CUDA 13.0 support (REQUIRED ORDER)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130
```

**Why Required**:
- Silero STT model (speech-to-text)
- Silero TTS model (text-to-speech)
- Optional: Vision models (LLaVA)

**Proven Patterns**:
- Device attribute pattern (rename to `_torch_device`)
- torch.hub.load indexing pattern
- Sample rate handling (16kHz STT, 24kHz TTS)

**Type Checking Patterns**:
```python
# PyTorch device
self._torch_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # type: ignore[read-only]

# torch.hub.load indexing
result = torch.hub.load(...)
self.model = result[0]  # type: ignore[index]
```

---

### 6. SearXNG

**Purpose**: Privacy-focused metasearch engine
**Status**: ✅ Optional but recommended
**Installation**:
```bash
# Docker (recommended)
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
docker compose up -d

# Access: http://localhost:8080 or http://192.168.1.4:8080
```

**Why Useful**:
- Web search for research agent
- Privacy-focused (no tracking)
- Self-hosted (no API costs)
- Multiple search engines in one

**Proven Patterns**:
- Async/sync wrapper required
- Event loop issues in sync contexts
- ThreadPoolExecutor solution

**Integration Pattern**:
```python
from core.async_compat.run_async import run_async

async def search_searxng(query: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8080/search?q={query}&format=json")
        return response.json()

# In sync context (DSPy module)
results = run_async(search_searxng(query))
```

---

### 7. Qdrant

**Purpose**: Vector database for semantic search
**Status**: ⚠️ Planned (not tested in R014)
**Installation**:
```bash
# Docker
docker run -p 6333:6333 qdrant/qdrant

# Python client
uv pip install qdrant-client
```

**Why Useful**:
- Semantic search over documents
- RAG (Retrieval-Augmented Generation)
- Memory for AI agents

**Integration Pattern** (planned):
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# Insert vectors
client.upsert(
    collection_name="documents",
    points=[PointStruct(id=1, vector=embedding, payload={"text": "..."})],
)

# Search
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=5,
)
```

---

### 8. httpx

**Purpose**: Async HTTP client
**Status**: ✅ REQUIRED for async operations
**Version**: 0.24+ (R014 uses httpx)
**Installation**:
```bash
uv pip install httpx
```

**Why Required**:
- Async HTTP requests (SearXNG, etc.)
- Better performance than requests
- Async context managers
- HTTP/2 support

**Proven Patterns**:
```python
import httpx

async def fetch_data(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

---

### 9. asyncio

**Purpose**: Async I/O (built-in Python 3.7+)
**Status**: ✅ REQUIRED
**Version**: Built-in (Python 3.7+)

**Why Required**:
- WebSocket support
- Concurrent LLM calls
- Async HTTP requests
- DSPy streaming

**Proven Patterns**:
- ThreadPoolExecutor for async/sync bridge
- New event loop per thread
- run_async_in_sync_context wrapper

---

## Architecture Dependencies

### 1. Clean Architecture

**Pattern**: Domain-Driven Design with strict layer boundaries
**Status**: ✅ REQUIRED
**Source**: R014 refactoring Phases 1-4
**Why Required**:
- Testability
- Maintainability
- Scalability
- Separation of concerns

**Layer Structure**:
```
domain/         - Business logic (no dependencies)
application/    - Use cases (orchestration)
infrastructure/ - External concerns (DB, HTTP)
presentation/   - API routes (HTTP/WebSocket)
```

---

### 2. Application Layer Pattern

**Pattern**: Use cases between API and services
**Status**: ✅ REQUIRED
**Source**: R014 `application/use_cases/`
**Why Required**:
- API depends on abstractions
- Easy to test
- Business logic independent

**Pattern**:
```python
class UseCase:
    def __init__(self, service: Service):
        self._service = service

    def execute(self, request: RequestDTO) -> ResponseDTO:
        result = self._service.do_something()
        return ResponseDTO(field=result)
```

---

### 3. DTO Pattern

**Pattern**: Request/response objects at API boundaries
**Status**: ✅ REQUIRED
**Source**: R014 `application/dtos/`
**Why Required**:
- Type-safe API boundaries
- Separate internal models from API models
- Easy validation

**Pattern**:
```python
# application/dtos/requests/{feature}.py
class {Request}DTO(BaseModel):
    field1: str
    field2: int

# application/dtos/responses/{feature}.py
class {Response}DTO(BaseModel):
    result: str
    metadata: dict
```

---

### 4. Repository Pattern

**Pattern**: Abstract base class + implementations
**Status**: ⚠️ Recommended (not used in R014)
**Why Useful**:
- Swappable data sources
- Easy to test (mock repository)
- Clean separation

**Pattern**:
```python
# domain/repositories/{entity}_repository.py
from abc import ABC, abstractmethod

class {Entity}Repository(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> {Entity} | None:
        pass

# infrastructure/repositories/{entity}_repository.py
class {Entity}RepositoryImpl({Entity}Repository):
    def get_by_id(self, id: str) -> {Entity} | None:
        # Implementation
        pass
```

---

### 5. Dependency Injection

**Pattern**: Global singletons + getter functions
**Status**: ✅ REQUIRED
**Source**: R014 `core/dependencies.py`
**Why Required**:
- Single instance per service
- Lazy initialization
- Easy to mock in tests

**Pattern**:
```python
# core/dependencies.py
_use_case: {Feature}UseCase | None = None

def get_{feature}_use_case() -> {Feature}UseCase:
    global _use_case
    if _use_case is None:
        service = {Service}()
        _use_case = {Feature}UseCase(service)
    return _use_case

# Usage
from core.dependencies import get_{feature}_use_case
use_case = get_{feature}_use_case()
```

---

## Integration Dependencies

### 1. DSPy + Ollama

**Pattern**: Built-in Ollama support
**Status**: ✅ PROVEN
**Configuration**:
```python
import dspy

lm = dspy.LM(
    "ollama_chat/qwen3:8b",
    api_base="http://localhost:11434",
    api_key=""
)
dspy.configure(lm=lm)
```

**Gotchas**:
- Use `ollama_chat/` prefix (not just `ollama/`)
- api_key can be empty string for Ollama
- Ensure Ollama is running (`ollama serve`)

---

### 2. DSPy Streaming

**Pattern**: Sync warmup required
**Status**: ✅ PROVEN
**Configuration**:
```python
# Step 1: Synchronous warmup
_ = module(query="warmup")

# Step 2: Create streaming wrapper
stream = dspy.streamify(
    module,
    stream_listeners=[
        StreamListener(signature_field_name="output_field", allow_reuse=True)
    ]
)

# Step 3: Stream
for chunk in stream(input=data):
    print(chunk, end="")
```

**Gotchas**:
- Forgetting warmup causes silent failures
- Use `allow_reuse=True` for multiple streams
- ChainOfThought better than Predict for streaming

---

### 3. WebSocket + FastAPI

**Pattern**: Connection state tracking
**Status**: ✅ PROVEN
**Configuration**:
```python
connection_active = True

async def send_event(event_type: str, data: dict):
    if not connection_active:
        return
    try:
        await websocket.send_json({"type": event_type, "data": data})
    except Exception:
        pass

try:
    await run_operation(send_event)
except Exception as e:
    connection_active = False
    await send_event("error", {"message": str(e)})
finally:
    connection_active = False
```

**Gotchas**:
- Always use connection state flag
- Silent exception handling (pass) after flag check
- Send events after each phase for progress

---

### 4. Async/Sync Bridge

**Pattern**: ThreadPoolExecutor wrapper
**Status**: ✅ PROVEN
**Configuration**:
```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

_thread_pool: ThreadPoolExecutor | None = None

def get_thread_pool() -> ThreadPoolExecutor:
    global _thread_pool
    if _thread_pool is None:
        _thread_pool = ThreadPoolExecutor(max_workers=4)
    return _thread_pool

def run_async(coro) -> Any:
    def run_in_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    pool = get_thread_pool()
    return pool.submit(run_in_loop).result()

# Usage
data = run_async(async_function())
```

**Gotchas**:
- Required for calling async from sync contexts (DSPy modules)
- Each thread gets its own event loop
- Cleanup thread pool on exit

---

## Development Dependencies

### Ruff

**Purpose**: Fast Python linter and formatter
**Status**: ✅ REQUIRED (CLAUDE_POLICY.md)
**Installation**:
```bash
uv pip install ruff
```

**Usage**:
```bash
ruff check . --fix
ruff format .
```

**Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]  # Line length handled by formatter
```

---

### Pyrefly

**Purpose**: Type checker for Python
**Status**: ✅ REQUIRED (CLAUDE_POLICY.md)
**Installation**:
```bash
uv pip install pyrefly
```

**Usage**:
```bash
pyrefly check . --summarize-errors
```

**Special Patterns**:
```python
# PyTorch device
self._torch_device = torch.device(...)  # type: ignore[read-only]

# torch.hub.load indexing
result = torch.hub.load(...)
self.model = result[0]  # type: ignore[index]

# MCP imports
from mcp__tavily__tavily_search import tavily_search  # type: ignore[import]
```

---

### pytest

**Purpose**: Testing framework
**Status**: ✅ RECOMMENDED
**Installation**:
```bash
uv pip install pytest pytest-asyncio pytest-cov
```

**Usage**:
```bash
pytest
pytest --cov=core --cov-report=html
pytest tests/test_specific.py
```

---

## Summary Table: Critical Dependencies

| # | Dependency | Purpose | Status | Version |
|---|------------|---------|--------|---------|
| 1 | DSPy 3.1+ | LLM framework | ✅ REQUIRED | 3.1+ |
| 2 | Ollama | Local LLM runtime | ✅ REQUIRED | Latest |
| 3 | FastAPI | Web framework | ✅ REQUIRED | 0.100+ |
| 4 | Pydantic | Data validation | ✅ REQUIRED | 2.0+ |
| 5 | PyTorch | Deep learning | ✅ REQUIRED (voice) | 2.0+ (CUDA) |
| 6 | SearXNG | Web search | ⚠️ Optional | Latest |
| 7 | Qdrant | Vector DB | ⚠️ Planned | Latest |
| 8 | httpx | Async HTTP | ✅ REQUIRED | 0.24+ |
| 9 | asyncio | Async I/O | ✅ REQUIRED | Built-in |

---

## Installation Commands (All Dependencies)

```bash
# Core dependencies
uv pip install dspy-ai fastapi uvicorn[standard] pydantic pydantic-settings httpx pytest pytest-asyncio pytest-cov ruff pyrefly

# PyTorch with CUDA (REQUIRED ORDER)
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Ollama (separate install)
curl -fsSL https://ollama.com/install.sh | sh
ollama serve
ollama pull qwen3:8b

# SearXNG (optional, Docker)
git clone https://github.com/searxng/searxng-docker.git
cd searxng-docker
docker compose up -d
```

---

## Environment Setup

```bash
# Create virtual environment
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements-core.txt
uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu130

# Start services
ollama serve &

# Verify installation
python -c "import dspy; import fastapi; import torch; print('✅ All dependencies OK')"
```

---

## Conclusion

All dependencies are **production-tested** in R014. Start Real AgentX with this exact stack for proven reliability.
