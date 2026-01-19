# T102: Create Ollama LLM Adapter

**Phase**: 1
**Estimated Time**: 30 minutes
**Dependencies**: T001, T002
**Blocked By**: None

---

## Context

**LLD References**:
- `lld/infrastructure_adapters.md` - LLM adapter interface
- `lld/incremental_release_plan.md` - Phase 1: Ollama adapter

**Description**:
Creates Ollama LLM adapter for local inference. This adapter provides async methods for text generation and streaming responses.

---

## Acceptance Criteria

**Passing Criteria**:
- OllamaLLMAdapter class exists
- Implements generate_response() for non-streaming
- Implements stream_response() for streaming
- Uses httpx for async HTTP calls
- Timeout configuration from Settings

**Verification Commands**:
```bash
cd /home/riju279/Documents/Code/XRIG/AgentX/prototypes/R013_travel_planning_stream/backend

# Verify adapter file exists
test -f agentx/infrastructure/external/ollama_llm.py && echo "Ollama adapter exists"

# Verify import works
python3 -c "from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter; print('Import OK')"
```

---

## Implementation Steps

### Step 1: Create Ollama LLM adapter

Create file `agentx/infrastructure/external/ollama_llm.py`:

```python
"""Ollama LLM adapter for local inference."""

import asyncio
import logging
from typing import AsyncIterator, Dict, Any, Optional, List
import httpx

from agentx.core.config import get_settings


logger = logging.getLogger(__name__)


class ModelInfo:
    """Information about the LLM model."""

    def __init__(
        self,
        name: str,
        base_url: str,
        context_size: int = 2048,
        supports_streaming: bool = True
    ):
        self.name = name
        self.base_url = base_url
        self.context_size = context_size
        self.supports_streaming = supports_streaming

    def __repr__(self) -> str:
        return f"ModelInfo(name={self.name}, base_url={self.base_url})"


class OllamaLLMAdapter:
    """Adapter for Ollama local LLM inference."""

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: int = 120
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout_seconds
        self._client: Optional[httpx.AsyncClient] = None
        self._model_info: Optional[ModelInfo] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def get_model_info(self) -> ModelInfo:
        """Get information about the model."""
        if self._model_info:
            return self._model_info

        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()

            # Find model in list
            models = data.get("models", [])
            model_details = None
            for m in models:
                if m.get("name", "").startswith(self.model):
                    model_details = m
                    break

            self._model_info = ModelInfo(
                name=self.model,
                base_url=self.base_url,
                context_size=2048,  # Default for most models
                supports_streaming=True
            )
            return self._model_info

        except Exception as e:
            logger.warning(f"Could not fetch model info: {e}")
            # Return default info
            self._model_info = ModelInfo(
                name=self.model,
                base_url=self.base_url
            )
            return self._model_info

    async def generate_response(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> str:
        """Generate a non-streaming response.

        Args:
            prompt: The main prompt to send
            context: Conversation history as list of {"role": "user/assistant", "content": "..."}
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        # Build messages list
        messages = []
        for msg in context:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            message = data.get("message", {})
            return message.get("content", "")

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error from Ollama: {e}")
            raise

    async def stream_response(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512
    ) -> AsyncIterator[str]:
        """Generate a streaming response.

        Args:
            prompt: The main prompt to send
            context: Conversation history
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they arrive
        """
        messages = []
        for msg in context:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        messages.append({
            "role": "user",
            "content": prompt
        })

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }

        try:
            async with self.client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        import json
                        data = json.loads(line)
                        if "message" in data:
                            content = data["message"].get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama stream failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Ollama stream: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Ollama is accessible."""
        try:
            response = await self.client.get("/")
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = await self.client.get("/api/tags")
            response.raise_for_status()
            data = response.json()
            models = data.get("models", [])
            return [m.get("name", "") for m in models]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def __repr__(self) -> str:
        return f"OllamaLLMAdapter(base_url={self.base_url}, model={self.model})"


# Factory function
async def create_ollama_adapter() -> OllamaLLMAdapter:
    """Create Ollama adapter from settings."""
    settings = get_settings()
    adapter = OllamaLLMAdapter(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds
    )

    # Verify connection
    if not await adapter.health_check():
        logger.warning(f"Ollama not accessible at {settings.ollama_base_url}")

    return adapter
```

### Step 2: Update infrastructure/external/__init__.py

Update file `agentx/infrastructure/external/__init__.py`:

```python
"""External infrastructure adapters."""

from agentx.infrastructure.external.qdrant_vector_store import QdrantVectorStoreAdapter
from agentx.infrastructure.external.redis_session_adapter import RedisSessionAdapter
from agentx.infrastructure.external.sqlite_session_adapter import SQLiteSessionAdapter
from agentx.infrastructure.external.in_memory_ui_repository import InMemoryUIComponentRepository
from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter, create_ollama_adapter

__all__ = [
    "QdrantVectorStoreAdapter",
    "RedisSessionAdapter",
    "SQLiteSessionAdapter",
    "InMemoryUIComponentRepository",
    "OllamaLLMAdapter",
    "create_ollama_adapter",
]
```

### Step 3: Update dependencies (T003) to include Ollama adapter getter

Update file `agentx/core/dependencies.py`:

Add to existing dependencies:

```python
def get_ollama_adapter():
    """Get Ollama LLM adapter instance."""
    from agentx.infrastructure.external.ollama_llm import create_ollama_adapter
    import asyncio

    # Note: This creates a new instance each time
    # For production, use a singleton with proper lifecycle
    adapter = OllamaLLMAdapter(
        base_url=get_settings().ollama_base_url,
        model=get_settings().ollama_model,
        timeout_seconds=get_settings().ollama_timeout_seconds
    )
    return adapter
```

---

## Expected Failures & Countermeasures

### Failure: Ollama not running

**Likelihood**: High
**Symptoms**: `httpx.ConnectError: Connection refused`

**Countermeasures**:
1. Start Ollama: `ollama serve`
2. Check Ollama status: `curl http://localhost:11434/`
3. Pull required model: `ollama pull gemma3:4b`

**Recovery Time**: 3 minutes

### Failure: Model not found

**Likelihood**: Medium
**Symptoms**: `Ollama request failed: 404` or model not in list

**Countermeasures**:
1. List available models: `ollama list`
2. Pull required model: `ollama pull gemma3:4b`
3. Update .env to use available model

**Recovery Time**: 5 minutes

### Failure: Timeout on large requests

**Likelihood**: Medium
**Symptoms**: `httpx.ReadTimeout` or streaming stops mid-response

**Countermeasures**:
1. Increase timeout in .env: `OLLAMA_TIMEOUT_SECONDS=300`
2. Reduce max_tokens parameter
3. Check Ollama logs: `docker logs ollama` (if using Docker)

**Recovery Time**: 2 minutes

---

## Retroactive Measures

### Upstream Drift Recovery

**Scenario**: T002 Settings changed (ollama_base_url renamed)
**Detection**: AttributeError when accessing settings.ollama_base_url
**Action**: Re-run T002 or update field name in create_ollama_adapter()

**Recovery Time**: 3 minutes

### Downstream Impact

**Scenario**: Ollama API changes
**Prevention**: Ollama API /api/chat is stable, but monitor changes
**Mitigation**: Add version detection to adapter
**Affected Tasks**: T200-T299 (Phase 2: Agent Layer)

---

## Artifacts

**Files Created**:
- `agentx/infrastructure/external/ollama_llm.py` (Ollama adapter, not locked - may need updates)

**Files Modified**:
- `agentx/infrastructure/external/__init__.py` (Add export)
- `agentx/core/dependencies.py` (Add get_ollama_adapter)

**Locked APIs**:
- `OllamaLLMAdapter` class name
- `generate_response()` method signature
- `stream_response()` method signature (async iterator pattern)
- `create_ollama_adapter()` factory function signature

---

## Quality Gates

**Quality Checks**:
- **Check**: Adapter file exists
  - Command: `test -f agentx/infrastructure/external/ollama_llm.py && echo "Ollama adapter exists"`
  - Expected: `Ollama adapter exists`
  - Required: Yes

- **Check**: Import works
  - Command: `python3 -c "from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter; print('OK')"`
  - Expected: `OK`
  - Required: Yes

- **Check**: Adapter can be instantiated
  - Command: `python3 -c "from agentx.infrastructure.external.ollama_llm import OllamaLLMAdapter; a = OllamaLLMAdapter('http://localhost:11434', 'gemma3:4b'); print(repr(a))"`
  - Expected: `OllamaLLMAdapter(base_url=http://localhost:11434, model=gemma3:4b)`
  - Required: Yes

---

## Notes

1. Ollama adapter uses httpx for async HTTP (not aiohttp)
2. Streaming uses async iterator pattern (AsyncIterator[str])
3. health_check() for monitoring systems
4. list_models() for debugging and model discovery
5. Client lazy initialization (created on first use)
6. close() method for cleanup (not used in Phase 1, needed in Phase 2+)

---

## Completion Checklist

- [ ] OllamaLLMAdapter class created
- [ ] generate_response() method implemented
- [ ] stream_response() method implemented (async iterator)
- [ ] health_check() method implemented
- [ ] list_models() method implemented
- [ ] create_ollama_adapter() factory function created
- [ ] Exported in infrastructure/external/__init__.py
- [ ] Added to core/dependencies.py
- [ ] Import tests pass
- [ ] Ready for T103 (Update DI Container)

---

**Task T102 is part of Phase 1: Domain + Infrastructure**
**Locked APIs**: OllamaLLMAdapter class name, method signatures
