# AGENTX

> A true personal AI assistant with memory, reasoning, and multimodal capabilities - your path to JARVIS.

## 🎯 Vision

AGENTX is designed to be a **full-on JARVIS** - a personal AI assistant that:

- **Handles your companies** and their dataflows
- **Actively provides warnings and updates** about your personal/professional life
- **Remembers everything** with time-aware retrieval (ColBERTv2 + Qdrant RAG)
- **Runs locally** with privacy-first architecture (Ollama + DSPy)
- **Scales to production** on NVIDIA DGX Spark infrastructure

## 🏗️ Architecture

```bash
┌─────────────────────────────────────────────────────────────┐
│                     AGENTX Core System                      │
│  (DSPy + Mem0AI + ColBERTv2 + Temporal RAG)                 │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Memory     │    │   Plugins    │    │  Frontend    │
│  (Mem0AI)    │    │  (FastMCP)   │    │   (PWA)      │
└──────────────┘    └──────────────┘    └──────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Qdrant      │    │   SearXNG    │    │   Ollama     │
│  (Vector DB) │    │  (Search)    │    │  (Local LLM) │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Development Machine:**
  - RTX 3060 12GB VRAM
  - 32GB RAM
  - Ryzen 5700X CPU
  - Ubuntu Linux

- **Production (DGX Spark):**
  - 500GB+ VRAM
  - 2TB+ NVMe SSD
  - 10Gbps network

### Installation

```bash
# Clone repository
git clone https://github.com/yourorg/agentx.git
cd agentx

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start Ollama
ollama serve

# Pull required models
ollama pull llama3.2
ollama pull llava:latest
ollama pull glm-4.7

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Run AGENTX
python main.py
```

## 📦 Technology Stack

### Core AI

| Component | Technology | Purpose |
| ----------- | ------------ | --------- |
| **LLM Framework** | [DSPy 3.1+](https://dspy.ai/) | Programmatic LLM interactions |
| **Memory** | [Mem0AI 1.0+](https://docs.mem0.ai/) | Long-term memory with episodic/semantic/procedural |
| **RAG** | ColBERTv2 + Qdrant | Late interaction embeddings |
| **Local LLM** | [Ollama](https://ollama.com/) | Privacy-first local inference |
| **Vector DB** | [Qdrant](https://qdrant.tech/) | High-performance vector search |

### Plugins

| Plugin | Technology | Purpose |
| -------- | ------------ | --------- |
| **Framework** | [FastMCP 2.0](https://gofastmcp.com/) | MCP server framework |
| **Search** | [SearXNG](https://searxng.org/) | Privacy-respecting web search |
| **Vision** | LLaVA + ColPali | Multimodal understanding |
| **Voice** | Whisper + Piper | STT/TTS capabilities |

### Frontend

| Component | Technology | Purpose |
| ----------- | ------------ | --------- |
| **Framework** | [Vercel AI SDK](https://ai-sdk.dev/) | Unified AI integration |
| **UI** | Next.js PWA | Progressive web app |
| **Styling** | Tailwind CSS | Utility-first styling |

## 📚 Research Documentation

Comprehensive research documentation is available in [`docs/research/`](docs/research/):

### Core Research

| Document | Description |
| ----------- | ------------ |
| [00_research_summary.md](docs/research/00_research_summary.md) | Project overview and architecture |
| [01_colbert_qdrant_guide.md](docs/research/01_colbert_qdrant_guide.md) | ColBERTv2 + Qdrant integration |
| [02_dspy_mem0_integration.md](docs/research/02_dspy_mem0_integration.md) | DSPy + Mem0 memory system |
| [03_ollama_local_llm.md](docs/research/03_ollama_local_llm.md) | Ollama local LLM deployment |

### Integration & Plugins

| Document | Description |
| ----------- | ------------ |
| [04_plugin_architecture.md](docs/research/04_plugin_architecture.md) | Core + Plugin design pattern |
| [05_mcp_integration.md](docs/research/05_mcp_integration.md) | Model Context Protocol integration |
| [11_fastmcp_guide.md](docs/research/11_fastmcp_guide.md) | FastMCP 2.0 complete guide |

### Frontend & UI

| Document | Description |
| ----------- | ------------ |
| [06_pwa_frontend.md](docs/research/06_pwa_frontend.md) | Progressive Web App frontend |
| [10_generative_ui_ollama_models.md](docs/research/10_generative_ui_ollama_models.md) | Generative UI with Ollama models |

### Advanced Features

| Document | Description |
| ----------- | ------------ |
| [07_temporal_rag.md](docs/research/07_temporal_rag.md) | Time-aware memory systems |
| [08_tts_stt_integration.md](docs/research/08_tts_stt_integration.md) | Voice interaction (TTS/STT) |
| [09_computer_vision.md](docs/research/09_computer_vision.md) | Visual understanding |

## 🧩 Plugin System

AGENTX uses a **Core + Plugin** architecture with FastMCP 2.0:

### Available Plugins

#### Company MIS Plugin

```python
@mcp.tool
def get_company_metrics(metric: str, period: str) -> dict:
    """Retrieve company financial and operational data."""
    return query_company_mis(metric, period)
```

#### SearXNG Search Plugin

```python
@mcp.tool
def web_search(query: str, categories: list[str]) -> list[dict]:
    """Search the web using SearXNG."""
    return searxng_search(query, categories)
```

#### Vision Plugin

```python
@mcp.tool
def analyze_image(image_path: str, task: str) -> dict:
    """Analyze image with vision model."""
    return vision_model.analyze(image_path, task)
```

### Creating Custom Plugins

See [Plugin Development Guide](docs/research/04_plugin_architecture.md) and [FastMCP Guide](docs/research/11_fastmcp_guide.md).

## 🧠 Memory System

AGENTX features a sophisticated **Temporal RAG** system:

- **Time-aware retrieval** - Understands when information was created
- **Fact invalidation** - New information overrides old
- **Duration tracking** - Long-term states vs point events
- **Memory consolidation** - Summarization over time periods
- **Four logical networks** - World, Bank, Opinion, Observation (Hindsight architecture)

See [Temporal RAG Guide](docs/research/07_temporal_rag.md) for details.

## 🎤 Voice Interaction

Full voice interface support:

- **Speech-to-Text** - Whisper (faster-whisper) for transcription
- **Text-to-Speech** - Piper for local synthesis
- **Voice Activity Detection** - Barge-in support for natural conversations
- **Real-time streaming** - <800ms mouth-to-ear latency

See [TTS/STT Integration Guide](docs/research/08_tts_stt_integration.md) for details.

## 👁️ Vision Capabilities

Multimodal understanding:

- **General understanding** - LLaVA for images and screenshots
- **Document analysis** - ColPali for document retrieval
- **Object detection** - YOLO for real-time detection
- **UI/UX analysis** - Screenshot understanding

See [Computer Vision Guide](docs/research/09_computer_vision.md) for details.

## 💻 Development

### Project Structure

```bash
agentx/
├── core/                    # Core AGENTX system
│   ├── agentx.py           # Main agent logic
│   ├── memory.py           # Memory management
│   └── rag.py              # RAG implementation
├── plugins/                 # FastMCP plugins
│   ├── company_mis/        # Company MIS integration
│   ├── searxng/            # Search integration
│   └── vision/             # Vision capabilities
├── frontend/               # PWA frontend
│   ├── app/                # Next.js app
│   └── components/         # React components
├── docs/                   # Documentation
│   └── research/          # Research docs
└── tests/                  # Tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test suite
pytest tests/test_memory.py

# Run with coverage
pytest --cov=core --cov-report=html
```

### Development Mode

```bash
# Start with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with debug logging
LOG_LEVEL=debug python main.py
```

## 🚢 Deployment

### Local Development

```bash
# Start all services locally
docker-compose up -d

# Or run services individually
ollama serve &
docker run -p 6333:6333 qdrant/qdrant &
python main.py
```

### Production (DGX Spark)

```bash
# Build Docker images
docker build -t agentx:latest .

# Deploy to Kubernetes
kubectl apply -f k8s/deployment.yaml

# Scale horizontally
kubectl scale deployment agentx --replicas=10
```

### Environment Variables

```bash
# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
VISION_MODEL=llava:latest

# Database
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=agentx_memory

# Search
SEARXNG_URL=http://192.168.1.4:8080

# Application
LOG_LEVEL=INFO
MAX_TOKENS=128000
TEMPERATURE=0.7
```

## 🔐 Security

- **Local-first** - All data processed locally by default
- **Encrypted storage** - Sensitive data encrypted at rest
- **OAuth authentication** - Enterprise-ready OAuth 2.1
- **Sandboxed plugins** - Plugins run in isolated environments
- **Rate limiting** - Built-in protection against abuse

## 📊 Performance

### Development Machine (RTX 3060)

| Operation | Latency | Throughput |
| ----------- | --------- | ------------ |
| Simple response | 2-4s | ~5 queries/min |
| Tool calling | 3-6s | ~3 queries/min |
| Vision analysis | 5-10s | ~1 query/min |

### Production System (DGX Spark)

| Operation | Latency | Throughput |
| ----------- | --------- | ------------ |
| Simple response | 500ms-2s | ~50 queries/min |
| Tool calling | 1-3s | ~20 queries/min |
| Vision analysis | 2-5s | ~10 queries/min |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [DSPy](https://dspy.ai/) - Programmatic LLM framework
- [Mem0AI](https://docs.mem0.ai/) - Memory layer for AI
- [Qdrant](https://qdrant.tech/) - Vector database
- [Ollama](https://ollama.com/) - Local LLM inference
- [FastMCP](https://gofastmcp.com/) - MCP server framework
- [Prefect](https://prefect.io/) - Workflow orchestration

## 📞 Support

For questions, issues, or contributions:

- 📖 [Documentation](docs/research/README.md)
- 🐛 [Issues](https://github.com/yourorg/agentx/issues)
- 💬 [Discussions](https://github.com/yourorg/agentx/discussions)

---

**Built with ❤️ using DSPy + Mem0AI + FastMCP + Ollama**

*Last updated: January 2025*
