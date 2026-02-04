# Mem0AI Open Source Configuration

**Source:** https://docs.mem0.ai/open-source/configuration
**Retrieved:** 2025-02-04

---

## Overview

Wire up Mem0 OSS with your preferred LLM, vector store, embedder, and reranker.

---

## Install Dependencies

### Install Mem0 OSS

```bash
pip install mem0ai
```

### Add Provider SDKs

```bash
pip install qdrant-client openai
```

### Clone Docker Compose

```bash
git clone https://github.com/mem0ai/mem0.git
cd mem0/examples/docker-compose
```

### Install Local Overrides

```bash
pip install -r requirements.txt
```

---

## Define Your Configuration

### Configuration Dictionary

```python
from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {"host": "localhost", "port": 6333},
    },
    "llm": {
        "provider": "openai",
        "config": {"model": "gpt-4.1-mini", "temperature": 0.1},
    },
    "embedder": {
        "provider": "vertexai",
        "config": {"model": "textembedding-gecko@003"},
    },
    "reranker": {
        "provider": "cohere",
        "config": {"model": "rerank-english-v3.0"},
    },
}

memory = Memory.from_config(config)
```

### Environment Variables for Secrets

```bash
export QDRANT_API_KEY="..."
export OPENAI_API_KEY="..."
export COHERE_API_KEY="..."
```

### YAML Configuration File

```yaml
vector_store:
  provider: qdrant
  config:
    host: localhost
    port: 6333

llm:
  provider: azure_openai
  config:
    api_key: ${AZURE_OPENAI_KEY}
    deployment_name: gpt-4.1-mini

embedder:
  provider: ollama
  config:
    model: nomic-embed-text

reranker:
  provider: zero_entropy
  config:
    api_key: ${ZERO_ENTROPY_KEY}
```

### Load Config File

```python
from mem0 import Memory

memory = Memory.from_config_file("config.yaml")
memory.add(["Remember my favorite cafe in Tokyo."], user_id="alex")
memory.search("favorite cafe", user_id="alex")
```

---

## Tune Component Settings

### Vector Store Collections

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "my_collection"  # Custom collection name
        },
    },
}
```

### LLM Extraction Temperature

```python
config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4.1-mini",
            "temperature": 0.1,  # Controls extraction randomness
        },
    },
}
```

### Reranker Depth (top_k)

```python
config = {
    "reranker": {
        "provider": "cohere",
        "config": {
            "model": "rerank-english-v3.0",
            "top_k": 5,  # Number of results to return after reranking
        },
    },
}
```

---

## Provider Options

### Vector Store Providers

| Provider | Config Keys |
|----------|-------------|
| **qdrant** | host, port, collection_name |
| **chroma** | persist_directory, collection_name |
| **pgvector** | connection_string, collection_name |
| **faiss** | index_path |

### LLM Providers

| Provider | Config Keys |
|----------|-------------|
| **openai** | model, temperature, api_key |
| **azure_openai** | api_key, deployment_name, endpoint |
| **ollama** | model, host |
| **groq** | model, api_key |

### Embedder Providers

| Provider | Config Keys |
|----------|-------------|
| **openai** | model, api_key |
| **ollama** | model, host |
| **vertexai** | model, project_id |
| **huggingface** | model |

### Reranker Providers

| Provider | Config Keys |
|----------|-------------|
| **cohere** | model, api_key |
| **zero_entropy** | api_key |
| **huggingface** | model |

---

## Ollama Configuration Example

For AGENTX using Ollama:

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agentx_memories"
        },
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "gemma3:4b",
            "host": "http://localhost:11434",
            "temperature": 0.7
        },
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "host": "http://localhost:11434"
        },
    },
}

memory = Memory.from_config(config)
```

---

## Quick Recovery

### Common Issues

**Issue**: Unknown reranker provider
**Fix**: `pip install --upgrade mem0ai`

**Issue**: Qdrant connection refused
**Fix**: Ensure Qdrant is running on port 6333

**Issue**: OpenAI API errors
**Fix**: Verify API key is set correctly

---

## Configuration for AGENTX

### Recommended Configuration

```yaml
# config/mem0.yaml
vector_store:
  provider: qdrant
  config:
    host: localhost
    port: 6333
    collection_name: agentx_memories

llm:
  provider: ollama
  config:
    model: gemma3:4b
    host: http://localhost:11434
    temperature: 0.7

embedder:
  provider: ollama
  config:
    model: nomic-embed-text
    host: http://localhost:11434

# No reranker for local deployment (optional)
# reranker:
#   provider: cohere
#   config:
#     model: rerank-english-v3.0
#     api_key: ${COHERE_API_KEY}
```

### Usage Pattern

```python
from mem0 import Memory

# Load from config file
memory = Memory.from_config_file("config/mem0.yaml")

# Or use environment config
memory = Memory.from_config(config)

# Add memories
memory.add(["User prefers Python over JavaScript"], user_id="user123")

# Search memories
results = memory.search("programming preference", user_id="user123")

# Get all memories
all_memories = memory.get_all(user_id="user123")
```

---

## Best Practices

1. **Use separate collections per environment** (dev, prod, testing)
2. **Set appropriate temperature** (lower for factual, higher for creative)
3. **Configure top_k** based on your use case (3-5 for focused, 10+ for comprehensive)
4. **Handle provider failures gracefully** with fallbacks
5. **Use environment variables for all API keys**
