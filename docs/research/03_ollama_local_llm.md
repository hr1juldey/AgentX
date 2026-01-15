# Ollama Integration Guide for Local LLMs

## Overview

Ollama is a self-hosted LLM runner that enables local execution of large language models. AGENTX uses Ollama as the primary inference engine for privacy, cost control, and offline capability.

## Why Ollama?

### Advantages
- **Complete privacy** - All data stays on your machine
- **No API costs** - Free after initial setup
- **Offline capability** - Works without internet
- **DSPy native support** - Direct integration via LiteLLM
- **Wide model support** - Llama, Mistral, Phi, Qwen, and more
- **Easy deployment** - Single command to run models

### Trade-offs
- **Hardware dependent** - Requires capable GPU/CPU
- **Slower than cloud** - Limited by local hardware
- **Model management** - Manual updates and storage

## Installation

### Quick Install

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Verify Installation

```bash
ollama --version
# Output: ollama version is 0.5.7
```

## Recommended Models

### For AGENTX

| Model | Size | RAM/VRAM | Best For |
|-------|------|----------|----------|
| llama3.2 | 3B | 8GB | General purpose, fast |
| llama3.2 | 11B | 16GB | Better reasoning |
| mistral-nemo | 12B | 16GB | Instruction following |
| qwen2.5 | 14B | 20GB | Multilingual |
| phi4 | 14B | 20GB | Efficiency |

### Pull Models

```bash
# Primary model
ollama pull llama3.2

# Embedding model
ollama pull nomic-embed-text

# Optional: specialized models
ollama pull mistral-nemo
ollama pull qwen2.5
ollama pull phi4
```

## DSPy Integration

### Basic Setup

```python
import dspy

# Configure Ollama
lm = dspy.LM(
    model="ollama/llama3.2",
    api_base="http://localhost:11434",
    api_key=""  # Ollama doesn't require API key
)

dspy.configure(lm=lm)

# Test
response = dspy.Predict("question -> answer")(
    question="What is DSPy?"
)
print(response.answer)
```

### Multiple Models

```python
# Configure different models for different tasks
reasoning_lm = dspy.LM(
    model="ollama/mistral-nemo",
    api_base="http://localhost:11434"
)

fast_lm = dspy.LM(
    model="ollama/llama3.2",
    api_base="http://localhost:11434"
)

# Use specific LM for modules
with dspy.context(lm=reasoning_lm):
    complex_agent = dspy.ReAct("question -> answer")

with dspy.context(lm=fast_lm):
    simple_agent = dspy.Predict("question -> answer")
```

### Embedding Model

```python
from dspy import Example
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configure embedding
embedder = dspy.Embedder(
    model="ollama/nomic-embed-text",
    api_base="http://localhost:11434"
)

# Generate embeddings
text = "User prefers Italian food"
embedding = embedder([text])[0]

# Store in Qdrant
client = QdrantClient(url="http://localhost:6333")
client.upsert(
    collection_name="memories",
    points=[
        PointStruct(
            id=1,
            vector=embedding,
            payload={"text": text}
        )
    ]
)
```

## Mem0AI + Ollama

### Configuration

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "ollama_base_url": "http://localhost:11434",
            "temperature": 0.1,
            "max_tokens": 2048
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434",
            "embedding_dims": 768
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": 6333,
            "collection_name": "agentx_memory"
        }
    }
}

memory = Memory.from_config(config)
```

### Usage

```python
# Add memory
memory.add(
    "User prefers Italian food, especially pasta carbonara",
    user_id="alice",
    metadata={"category": "preference"}
)

# Search memory
results = memory.search(
    "What food does the user like?",
    user_id="alice"
)
```

## Performance Optimization

### GPU Acceleration

```bash
# Check GPU availability
ollama ps

# Run with GPU (automatic if available)
ollama run llama3.2
```

### Quantization

```bash
# Use quantized models for lower memory
# 4-bit quantization (Q4_K_M)
ollama pull llama3.2:3b-q4_K_M

# 8-bit quantization (Q8_0)
ollama pull llama3.2:3b-q8_0
```

### Batch Processing

```python
# Process multiple requests in parallel
import asyncio

async def process_batch(queries: list[str]):
    tasks = [
        dspy.AsyncPredict("question -> answer")(question=q)
        for q in queries
    ]
    results = await asyncio.gather(*tasks)
    return results

# Usage
results = asyncio.run(process_batch([
    "What's the weather?",
    "What's for dinner?",
    "Tell me a joke"
]))
```

### Model Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_predict(question: str) -> str:
    """Cache predictions for common queries."""
    response = dspy.Predict("question -> answer")(
        question=question
    )
    return response.answer

# First call: slow
result1 = cached_predict("What time is it?")

# Subsequent calls: instant
result2 = cached_predict("What time is it?")
```

## Advanced Configuration

### Custom Model File

```bash
# Create Modelfile
cat > Modelfile <<EOF
FROM llama3.2

# Set parameters
PARAMETER temperature 0.1
PARAMETER num_ctx 32768
PARAMETER num_gpu -1  # Use all GPU layers

# System prompt
SYSTEM You are AGENTX, a helpful AI assistant with long-term memory.
EOF

# Build custom model
ollama create agentx-base -f Modelfile

# Run custom model
ollama run agentx-base
```

### API Server

```bash
# Start Ollama server
ollama serve

# Configure for production
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_NUM_PARALLEL=4
export OLLAMA_MAX_LOADED_MODELS=3

# Start with custom config
ollama serve
```

### Model Management

```bash
# List installed models
ollama list

# Show model info
ollama show llama3.2

# Remove old models
ollama rm old-model

# Update model
ollama pull llama3.2 --verbose
```

## Monitoring

### Resource Usage

```bash
# Check running models
ollama ps

# Monitor with GPU
watch -n 1 nvidia-smi

# Check memory usage
ps aux | grep ollama
```

### Logging

```python
import logging

# Enable DSPy logging
dspy.enable_logging()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log predictions
with dspy.context(log=True):
    response = agent(user_input="Hello")
```

### Performance Metrics

```python
import time

def timed_predict(question: str) -> dict:
    """Measure prediction time."""
    start = time.time()

    response = dspy.Predict("question -> answer")(
        question=question
    )

    end = time.time()

    return {
        "answer": response.answer,
        "latency": end - start,
        "model": "ollama/llama3.2"
    }

# Usage
result = timed_predict("What is the capital of France?")
print(f"Response: {result['answer']}")
print(f"Latency: {result['latency']:.2f}s")
```

## Troubleshooting

### Issue: Out of Memory

```bash
# Solution 1: Use smaller model
ollama pull phi4:14b-q4_K_M

# Solution 2: Reduce context
ollama run llama3.2 --num_ctx 4096

# Solution 3: Enable GPU offloading
ollama run llama3.2 --num_gpu 50
```

### Issue: Slow Responses

```python
# Solution 1: Use smaller/faster model
lm = dspy.LM(model="ollama/phi4")

# Solution 2: Reduce max tokens
lm = dspy.LM(
    model="ollama/llama3.2",
    max_tokens=512
)

# Solution 3: Enable caching
@lru_cache(maxsize=50)
def fast_predict(question):
    return agent(question)
```

### Issue: Poor Quality Responses

```python
# Solution 1: Use Chain of Thought
cot = dspy.ChainOfThought("question -> answer")
response = cot(question="Complex query here")

# Solution 2: Add few-shot examples
trainset = [
    Example(question="Q1", answer="A1"),
    Example(question="Q2", answer="A2"),
]

optimizer = dspy.BootstrapFewShot()
optimized = optimizer.compile(
    dspy.Predict("question -> answer"),
    trainset=trainset
)
```

## NVIDIA DGX Spark Optimization

### Multi-GPU Setup

```bash
# Run on specific GPU
CUDA_VISIBLE_DEVICES=0 ollama serve

# Tensor parallelism (multi-GPU)
ollama run llama3.2 --num_gpu 4
```

### Model Sharding

```python
# Distribute model across GPUs
config = {
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "num_gpu": 4,  # Use 4 GPUs
            "num_thread": 32  # Use 32 CPU threads
        }
    }
}
```

### High-Throughput Configuration

```bash
# Increase parallel requests
export OLLAMA_NUM_PARALLEL=8

# Increase batch size
export OLLAMA_BATCH_SIZE=32

# Keep more models loaded
export OLLAMA_MAX_LOADED_MODELS=5
```

## References

- [Ollama Documentation](https://ollama.com/docs)
- [DSPy Ollama Integration](https://sieves.ai/guides/models/)
- [Ollama Model Library](https://ollama.com/library)
- [NVIDIA DGX Deployment Guide](https://www.nvidia.com/en-us/data-center/dgx-systems/)
