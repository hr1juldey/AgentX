# AGENTX: Research Summary & Architecture Overview

## Project Vision

AGENTX is a true personal assistant that handles companies and their dataflow, actively provides warnings and updates about personal/professional life activities. It features a ColBERTv2 IR-based Qdrant RAG system that remembers and retrieves everything on time.

## Core Architecture

### Memory-Enabled Ollama-Based Agent

The system runs on **Ollama** with local LLMs and **SearXNG** search engine, providing:
- **Long-term temporal RAG capacity** - remembers, tracks, and takes action based on data
- **User choice adaptation** - learns from user interactions and preferences
- **Core + Plugin architecture** - modular design for extensibility

### System Components

#### Core Layer
- **Memory-enabled agent** - Base functionality (chat and conversation)
- **DSPy** - Framework for programmatic LLM interactions
- **Mem0AI** - Long-term memory management
- **Qdrant** - Vector database for semantic search
- **ColBERTv2** - Late interaction embedding model via FastEmbed

#### Plugin Extensions
- **Internet Search** - SearXNG integration for web queries
- **Company MIS MCP** - Model Context Protocol for data manipulation
- **Personality System** - Multiple personality profiles
- **TTS/STT** - Text-to-Speech and Speech-to-Text
- **Computer Vision** - Image analysis and understanding
- **Additional capabilities** - Extensible plugin system

#### Frontend
- **Trusted PWA Client** - Progressive Web App for cross-platform access

---

## Technology Stack

### Dependencies (from req.txt)
```
dspy>=3.1.0              # Programmatic LLM framework
mem0ai>=1.0.2            # Memory layer for AI
fastembed>=0.7.4         # ColBERTv2 embeddings
qdrant-client>=1.16.2    # Vector database client
```

### Key Technologies

1. **DSPy 3.1+**
   - Turns LLMs into structured, type-safe Python functions
   - Declarative signatures for input/output
   - Built-in modules: Predict, ChainOfThought, ReAct
   - Optimizers: MIPROv2, BootstrapFewShot, KNN
   - Supports Ollama for local models

2. **Mem0AI 1.0+**
   - Long-term memory for AI agents
   - Persistent conversation history
   - User preference tracking
   - Memory categorization and tagging
   - Multi-user memory isolation

3. **FastEmbed 0.7+**
   - Late interaction text embeddings
   - ColBERTv2 support (128 dimensions)
   - ONNX-optimized for performance
   - Multi-vector representations
   - GPU acceleration support

4. **Qdrant 1.16+**
   - Vector similarity search
   - Multivector support for ColBERT
   - Hybrid queries (dense + sparse)
   - Temporal filtering
   - Quantization for storage efficiency

5. **Ollama Integration**
   - Local LLM deployment
   - Support for: Llama, Mistral, Phi, Qwen
   - API-compatible with OpenAI clients
   - DSPy native support via LiteLLM

6. **SearXNG**
   - Privacy-focused metasearch engine
   - Self-hosted on local network (http://192.168.1.4:8080)
   - JSON API for programmatic access
   - Category-based search

---

## Research References

### Documentation Sources
- [Qdrant FastEmbed ColBERT Guide](https://qdrant.tech/documentation/fastembed/fastembed-colbert/)
- [DSPy Mem0 ReAct Agent Tutorial](https://dspy.ai/tutorials/mem0_react_agent/)
- [ColBERTv2 Research Papers](https://arxiv.org/html/2601.07125v1)

### Key Findings

#### ColBERTv2 Architecture
- **Late interaction mechanism** - Token-level matching
- **MaxSim operation** - Maximum similarity scoring
- **Multi-vector representations** - One vector per token
- **Residual compression** - Reduced memory footprint
- **128-dimensional embeddings** - Efficient storage

#### Temporal RAG Systems
- **Time-aware retrieval** - Critical for evolving information
- **Memory hierarchy** - Episodic, Semantic, Procedural
- **Fact invalidation** - New information overrides old
- **Temporal reasoning** - "What happened before X?"
- **GraphRAG patterns** - Vector + Knowledge Graph

#### Plugin Architecture
- **Core + Plugin separation** - Minimal core, extensible plugins
- **MCP integration** - Model Context Protocol for tools
- **Dynamic tool discovery** - Runtime capability detection
- **Hot-swappable components** - No system restart required

#### Memory Systems
- **Hindsight architecture** - 91.4% on LongMemEval
- **TEMPR retrieval** - Parallel semantic + temporal
- **CARA dispositions** - Skepticism, literalism, empathy
- **Duration-aware construction** - Temporal knowledge graphs

---

## Implementation Priorities

### Phase 1: Core Foundation
1. DSPy + Ollama integration
2. Mem0 memory system setup
3. Qdrant + ColBERTv2 embeddings
4. Basic ReAct agent with memory

### Phase 2: Essential Plugins
1. SearXNG web search
2. MCP server integration
3. Basic TTS/STT
4. PWA frontend scaffold

### Phase 3: Advanced Features
1. Company MIS MCP integration
2. Computer vision plugin
3. Multi-personality system
4. Advanced temporal RAG

---

## Hardware Requirements

### NVIDIA DGX Spark
- **GPU**: Tesla/H100 architecture
- **Memory**: 500GB+ VRAM recommended
- **Storage**: 2TB+ NVMe SSD
- **Network**: 10Gbps for distributed queries

### Performance Considerations
- **ColBERTv2 inference**: ~200ms per document
- **Qdrant search**: <50ms for 1M vectors
- **Ollama LLM**: Variable (model-dependent)
- **Target latency**: <2s end-to-end response

---

## Next Steps

See individual research documents for detailed implementation guides:
- `01_colbert_qdrant_guide.md` - Embedding setup
- `02_dspy_mem0_integration.md` - Memory agent
- `03_ollama_local_llm.md` - Local model setup
- `04_plugin_architecture.md` - Core + Plugin design
- `05_mcp_integration.md` - Model Context Protocol
- `06_pwa_frontend.md` - Progressive Web App
- `07_temporal_rag.md` - Time-aware retrieval
- `08_tts_stt_integration.md` - Voice interfaces
- `09_computer_vision.md` - Visual understanding
