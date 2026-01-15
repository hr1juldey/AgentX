# FastMCP 2.0 Complete Guide for AGENTX

## Overview

**FastMCP 2.0** is the production-ready Python framework for building Model Context Protocol (MCP) servers, developed by Prefect. It extends far beyond the basic MCP SDK with enterprise features, advanced patterns, and deployment tooling specifically designed for building production-grade AI agents like AGENTX.

## Why FastMCP for AGENTX?

### The JARVIS Vision

Your goal is to build AGENTX as a full-on JARVIS with multimodal capabilities. FastMCP provides the perfect plugin architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     AGENTX Core                          │
│  (DSPy + Mem0AI + ColBERTv2 + Temporal RAG)              │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌───────────────────────────────┐
              │     FastMCP Plugin Hub        │
              │  (Standardized Tool Access)    │
              └───────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Company MIS  │    │  SearXNG     │    │  Vision      │
│   MCP Server │    │  MCP Server  │    │  MCP Server  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### FastMCP vs Official MCP SDK

| Feature | FastMCP 2.0 | Official MCP SDK |
|---------|-------------|------------------|
| **Basic Protocol** | ✅ Full support | ✅ Full support |
| **Enterprise Auth** | ✅ Google, GitHub, Azure, Auth0, WorkOS | ⚠️ Manual setup |
| **Server Composition** | ✅ Built-in mounting/importing | ❌ Manual |
| **OpenAPI/FastAPI Auto-gen** | ✅ One-line conversion | ❌ Manual |
| **Proxy Support** | ✅ Native proxying | ❌ Manual |
| **Deployment Tools** | ✅ FastMCP Cloud, CLI | ⚠️ Manual |
| **Testing Framework** | ✅ Built-in fixtures | ⚠️ Manual |
| **LLM Sampling** | ✅ With fallback handlers | ⚠️ Basic |
| **Storage Backends** | ✅ Pluggable (Redis, DynamoDB, etc.) | ❌ None |
| **Developer Experience** | ✅ `@mcp.tool` decorator | ⚠️ More verbose |

**Key Insight**: FastMCP 1.0 was incorporated into the official SDK in 2024. FastMCP 2.0 is the actively maintained production version that extends beyond basic protocol implementation.

## Installation

### Basic Installation

```bash
# Using pip
pip install fastmcp

# Using uv (recommended - 10-100x faster than pip)
uv pip install fastmcp

# With CLI extras
pip install "fastmcp[cli]"

# For development
pip install "fastmcp[dev]"
```

### System Requirements for AGENTX

**Development Machine (Current):**
- RTX 3060 12GB VRAM
- 32GB RAM
- Ryzen 5700X CPU
- Supports: Development, testing, small-scale deployments

**Production (DGX Spark):**
- 500GB+ VRAM
- 2TB+ NVMe SSD
- 10Gbps network
- Supports: Full multimodal AGENTX with all plugins

## Core Concepts

### 1. The FastMCP Server

```python
from fastmcp import FastMCP

# Create server with configuration
mcp = FastMCP(
    name="agentx-core",
    version="2.0.0",
    include_tags={"public", "api"},  # Only expose these tags
    exclude_tags={"internal", "deprecated"},
    on_duplicate_tools="error",  # Handle duplicates
)
```

### 2. Tools (Actions for LLMs)

Tools are like POST endpoints - they execute code and produce side effects.

```python
@mcp.tool
def search_database(query: str, limit: int = 10) -> list[dict]:
    """Search the company database for records.

    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)

    Returns:
        List of matching records
    """
    # Your implementation
    results = db.search(query, limit=limit)
    return results

@mcp.tool
async def process_payment(amount: float, currency: str = "USD") -> dict:
    """Process a payment transaction.

    This tool demonstrates async support and type hints.
    """
    result = await payment_gateway.charge(amount, currency)
    return result
```

**Tool Features:**
- ✅ Automatic schema generation from type hints
- ✅ Sync and async support
- ✅ Docstring becomes tool description
- ✅ Type validation with Pydantic
- ✅ Context injection (logging, progress, resources)

### 3. Resources (Data for LLMs)

Resources are like GET endpoints - they expose read-only data.

```python
@mcp.resource("config://system")
def get_system_config() -> dict:
    """Provides system configuration."""
    return {
        "version": "2.0.0",
        "features": ["memory", "vision", "voice"],
        "limits": {"max_tokens": 128000}
    }

@mcp.resource("data://employees/{id}")
def get_employee(id: str) -> str:
    """Get employee information by ID."""
    employee = db.get_employee(id)
    return json.dumps(employee)
```

### 4. Prompts (Reusable Templates)

Prompts are templates that guide LLM interactions.

```python
@mcp.prompt
def analyze_code(code: str) -> str:
    """Generate a code analysis prompt."""
    return f"""
    Analyze this code for:
    1. Security vulnerabilities
    2. Performance issues
    3. Best practices violations

    Code:
    {code}
    """
```

## Server Composition & Scaling

### Mounting Servers (Live Linking)

```python
from fastmcp import FastMCP

# Main AGENTX server
agentx = FastMCP("agentx-main")

# Mount external servers
agentx.mount_server("company-mis", company_mis_server)
agentx.mount_server("search", searxng_server)
agentx.mount_server("vision", vision_server)

# All tools from mounted servers available
agentx.run()
```

**Benefits:**
- Hot-reload plugin changes
- Independent deployment
- Namespace isolation
- Tag filtering per server

### Importing Servers (Static Composition)

```python
from fastmcp import FastMCP

agentx = FastMCP("agentx-main")

# Import tools from another server
agentx.import_server(mis_server, prefix="mis")
agentx.import_server(vision_server, prefix="vision")

# Tools available as:
# - mis.get_company_data
# - vision.analyze_image
```

### Server Proxying

```python
from fastmcp import FastMCP

# Create proxy to external MCP server
proxy = FastMCP("proxy-server")
proxy.add_proxy("http://external-mcp-server:8080")

# All external tools available through proxy
proxy.run()
```

**Use Cases:**
- Wrap existing MCP servers
- Add authentication layer
- Transform tool inputs/outputs
- Log all tool calls

## Authentication (Enterprise-Grade)

### OAuth 2.1 Support

FastMCP 2.12+ includes OAuth proxy for providers without Dynamic Client Registration:

```python
from fastmcp import FastMCP
from fastmcp.server.auth.azure import AzureProvider

mcp = FastMCP("agentx-auth")

# Configure OAuth
mcp.set_auth_provider(
    AzureProvider(
        tenant_id="your-tenant-id",
        client_id="your-client-id",
    )
)

# Run with authentication
mcp.run(transport="http", host="0.0.0.0", port=8000)
```

**Supported Providers:**
- ✅ Google
- ✅ GitHub
- ✅ Azure (Entra ID)
- ✅ Auth0
- ✅ WorkOS
- ✅ Keycloak

### Token Management

```python
from fastmcp.server.auth import TokenStorage

# Persistent token storage
storage = TokenStorage(
    backend="redis",  # or "dynamodb", "filesystem", "memory"
    encryption=True,
    ttl=3600  # Token refresh interval
)

mcp = FastMCP("agentx", auth_storage=storage)
```

### Authentication Patterns

**Pattern 1: API Key (Simple)**

```python
@mcp.tool
def protected_operation(api_key: str) -> dict:
    """Operation requiring API key."""
    if not validate_api_key(api_key):
        raise ValueError("Invalid API key")
    return perform_operation()
```

**Pattern 2: OAuth (Enterprise)**

```python
from fastmcp.server.auth.oauth_proxy import OAuthProxy

mcp = FastMCP("agentx")
mcp.set_auth_provider(
    GitHubProvider(
        client_id="github-client-id",
        client_secret="github-client-secret",
    )
)
```

**Pattern 3: JWT Validation**

```python
from fastmcp.server.auth.jwt import JWTVerifier

mcp = FastMCP("agentx")
mcp.set_auth_provider(
    JWTVerifier(
        issuer="https://your-auth.com",
        audience="agentx-api",
        public_key_path="keys.pem"
    )
)
```

## Deployment Options

### Transport Options

| Transport | Best For | Multi-Client | Network Access |
|-----------|----------|--------------|-----------------|
| **STDIO** | Local development, Claude Desktop | ❌ No | ❌ No |
| **HTTP (Streamable)** | Remote servers, cloud | ✅ Yes | ✅ Yes |
| **SSE** | Legacy compatibility | ✅ Yes | ✅ Yes |

### STDIO Transport (Local Development)

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("agentx-local")

@mcp.tool
def local_operation(data: str) -> str:
    return f"Processed: {data}"

if __name__ == "__main__":
    mcp.run()  # Default: STDIO
```

**Configuration (mcp.json):**
```json
{
  "mcpServers": {
    "agentx-local": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/agentx",
        "run", "server.py"
      ]
    }
  }
}
```

### HTTP Transport (Production)

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP("agentx-remote")

@mcp.tool
def remote_operation(query: str) -> dict:
    return {"result": f"Query: {query}"}

if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8080,
        path="/api/mcp/"
    )
```

**Client Connection:**
```json
{
  "mcpServers": {
    "agentx-remote": {
      "url": "http://agentx-server:8080/api/mcp/",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

### FastMCP Cloud (Managed Deployment)

```bash
# Install FastMCP CLI
pip install "fastmcp[cli]"

# Login to FastMCP Cloud
fastmcp login

# Deploy your server
fastmcp deploy

# Or deploy from GitHub repo
fastmcp deploy --repo https://github.com/yourorg/agentx
```

**Features:**
- ✅ Automatic builds from git
- ✅ PR previews on unique URLs
- ✅ Zero-downtime deployments
- ✅ Built-in monitoring
- ✅ Free while in beta

## FastAPI Integration

### Auto-Generate MCP from FastAPI

```python
# FastAPI app
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str
    limit: int = 10

@app.post("/search")
def search(query: Query) -> list[dict]:
    """Search the knowledge base."""
    return kb.search(query.text, query.limit)

@app.get("/config")
def get_config() -> dict:
    """Get system configuration."""
    return {"version": "2.0"}
```

**Convert to MCP in one line:**

```python
from fastmcp import FastMCP
from fastmcp.integrations.fastapi import from_fastapi

# Auto-generate MCP server
mcp = from_fastapi(
    app,
    name="agentx-api",
    path="/api/mcp/"  # Mount path
)

if __name__ == "__main__":
    mcp.run(transport="http", port=8080)
```

**Result:**
- All FastAPI routes become MCP tools
- Request models become tool parameters
- OpenAPI docs become tool descriptions
- Middleware and auth preserved

### Mounting in Existing FastAPI App

```python
from fastapi import FastAPI
from fastmcp import FastMCP
from fastmcp.integrations.fastapi import mount_to_app

app = FastAPI()
mcp = FastMCP("agentx-mcp")

# Add tools
@mcp.tool
def agentx_tool(data: str) -> str:
    return f"Processed: {data}"

# Mount MCP server into FastAPI
mount_to_app(
    mcp,
    app,
    path="/mcp",  # MCP endpoint path
    auth_required=True,  # Use FastAPI auth
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Advanced Features

### LLM Sampling (Server-Side LLM Calls)

Allow MCP servers to request LLM completions from clients:

```python
from fastmcp import FastMCP, Context
from pydantic import BaseModel

class SentimentResult(BaseModel):
    sentiment: str
    confidence: float
    reasoning: str

mcp = FastMCP("agentx-sampling")

@mcp.tool
async def analyze_sentiment(text: str, ctx: Context) -> SentimentResult:
    """Analyze text sentiment using client's LLM."""
    result = await ctx.sample(
        messages=f"Analyze sentiment: {text}",
        response_format=SentimentResult,
    )
    return result
```

**With Fallback Handler:**

```python
from fastmcp.client.sampling.handlers.openai import OpenAISamplingHandler
import os

mcp = FastMCP(
    "agentx-sampling",
    sampling_handler=OpenAISamplingHandler(
        default_model="gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY")
    ),
    sampling_handler_behavior="fallback",  # Use when client doesn't support sampling
)
```

### Storage Backends

```python
from fastmcp import FastMCP
from fastmcp.server.storage import StorageBackend

# Redis storage
storage = StorageBackend(
    type="redis",
    url="redis://localhost:6379",
    encryption=True,
    ttl=3600
)

# DynamoDB storage
storage = StorageBackend(
    type="dynamodb",
    table_name="agentx-state",
    region="us-east-1",
    encryption=True
)

mcp = FastMCP("agentx", storage=storage)

@mcp.tool
async def stateful_operation(key: str, value: str, ctx: Context) -> str:
    """Operation with persistent state."""
    # Store state
    await ctx.storage.set(key, value)
    # Retrieve later
    return await ctx.storage.get(key)
```

### Background Tasks

```python
from fastmcp import FastMCP
import asyncio

mcp = FastMCP("agentx-tasks")

@mcp.tool
async def long_running_task(task_id: str) -> str:
    """Start a long-running background task."""
    async def task():
        await asyncio.sleep(60)  # Simulate work
        return f"Task {task_id} complete"

    # Run in background
    mcp.create_task(task())
    return f"Task {task_id} started"
```

### Progress Reporting

```python
@mcp.tool
async def process_large_dataset(dataset_id: str, ctx: Context) -> dict:
    """Process dataset with progress updates."""
    total = 1000

    for i in range(total):
        # Process item
        await process_item(dataset_id, i)

        # Report progress
        await ctx.report_progress(i + 1, total)

    return {"status": "complete", "processed": total}
```

## Testing & Debugging

### MCP Inspector

```bash
# Install inspector
npm install -g @modelcontextprotocol/inspector

# Test STDIO server
mcp dev server.py

# Test HTTP server
mcp dev http://localhost:8080/api/mcp/
```

**Features:**
- Visual tool testing
- Resource browsing
- Prompt testing
- Real-time logs
- Connection history

### Unit Testing

```python
import pytest
from fastmcp import Client

async def test_search_tool():
    """Test the search tool."""
    client = Client("server.py")

    async with client:
        result = await client.call_tool(
            "search_database",
            {"query": "test", "limit": 5}
        )

        assert len(result) > 0
        assert all("id" in item for item in result)

async def test_resource_access():
    """Test resource access."""
    client = Client("server.py")

    async with client:
        config = await client.read_resource("config://system")

        assert config["version"] == "2.0.0"
```

### Debugging in VS Code

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug MCP Server",
      "type": "python",
      "request": "launch",
      "program": "server.py",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

## Configuration (fastmcp.json)

### Project Structure

```json
{
  "$schema": "https://fastmcp.com/schema.json",

  "source": {
    "type": "filesystem",
    "path": "server.py",
    "entrypoint": "mcp"
  },

  "environment": {
    "type": "uv",
    "python": ">=3.10",
    "dependencies": [
      "pandas",
      "numpy",
      "qdrant-client",
      "mem0ai"
    ]
  },

  "deployment": {
    "transport": "http",
    "host": "0.0.0.0",
    "port": 8080,
    "path": "/api/mcp/",
    "log_level": "INFO"
  }
}
```

**Running with config:**

```bash
fastmcp run fastmcp.json

# Or deploy
fastmcp deploy fastmcp.json
```

## Production Deployment

### Docker Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependencies
COPY requirements.txt .
RUN uv pip install -r requirements.txt

# Copy application
COPY . .

# Expose MCP port
EXPOSE 8080

# Run server
CMD ["python", "server.py"]
```

**docker-compose.yml:**

```yaml
version: '3.8'
services:
  agentx-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - TRANSPORT=http
      - HOST=0.0.0.0
      - PORT=8080
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agentx-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agentx-mcp
  template:
    metadata:
      labels:
        app: agentx-mcp
    spec:
      containers:
      - name: agentx-mcp
        image: agentx-mcp:latest
        ports:
        - containerPort: 8080
        env:
        - name: TRANSPORT
          value: "http"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: agentx-mcp-service
spec:
  selector:
    app: agentx-mcp
  ports:
  - port: 8080
    targetPort: 8080
  type: LoadBalancer
```

## Best Practices for AGENTX

### 1. Plugin Architecture

```python
# plugins/company_mis/server.py
from fastmcp import FastMCP

mis_mcp = FastMCP("company-mis")

@mis_mcp.tool
def get_metrics(metric: str) -> dict:
    """Get company metrics."""
    return fetch_metrics(metric)

# plugins/vision/server.py
from fastmcp import FastMCP

vision_mcp = FastMCP("agentx-vision")

@vision_mcp.tool
def analyze_image(image_path: str) -> dict:
    """Analyze image with vision model."""
    return vision_model.analyze(image_path)

# core/server.py
from fastmcp import FastMCP
from plugins.company_mis.server import mis_mcp
from plugins.vision.server import vision_mcp

agentx = FastMCP("agentx-core")

# Mount plugins
agentx.mount_server("mis", mis_mcp)
agentx.mount_server("vision", vision_mcp)

agentx.run(transport="http", port=8080)
```

### 2. Error Handling

```python
@mcp.tool
async def robust_operation(data: str) -> dict:
    """Operation with comprehensive error handling."""
    try:
        result = await process(data)
        return {
            "success": True,
            "data": result
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": "validation",
            "message": str(e)
        }
    except Exception as e:
        # Log to context
        ctx.error(f"Operation failed: {e}")
        return {
            "success": False,
            "error": "internal",
            "message": "Operation failed"
        }
```

### 3. Context Logging

```python
@mcp.tool
async def logged_operation(data: str, ctx: Context) -> str:
    """Operation with detailed logging."""
    ctx.debug(f"Starting operation with data: {data[:50]}...")
    ctx.info("Processing request")

    try:
        result = await process(data)
        ctx.info(f"Operation completed successfully")
        return result
    except Exception as e:
        ctx.error(f"Operation failed: {e}")
        raise
```

### 4. Tag-Based Filtering

```python
# Public tools
@mcp.tool(tags=["public", "api"])
def public_search(query: str) -> list:
    """Search available to everyone."""
    return search(query)

# Internal tools
@mcp.tool(tags=["internal", "admin"])
def system_cleanup() -> dict:
    """Internal system maintenance."""
    return cleanup()

# Server configuration
mcp = FastMCP(
    "agentx",
    include_tags={"public"},  # Only expose public tools
    exclude_tags={"deprecated"}
)
```

### 5. Type Safety

```python
from pydantic import BaseModel, Field

class SearchQuery(BaseModel):
    text: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100)
    filters: dict[str, str] = Field(default_factory=dict)

@mcp.tool
def typed_search(query: SearchQuery) -> list[dict]:
    """Type-safe search with validation."""
    return search(
        query.text,
        limit=query.limit,
        filters=query.filters
    )
```

## Performance Optimization

### Connection Pooling

```python
from fastmcp import FastMCP
import asyncio

class DatabasePool:
    def __init__(self):
        self.pool = asyncio.Queue(maxsize=10)

    async def get_connection(self):
        return await self.pool.get()

    async def return_connection(self, conn):
        await self.pool.put(conn)

mcp = FastMCP("agentx-pool")
db_pool = DatabasePool()

@mcp.tool
async def pooled_query(sql: str) -> list:
    """Query with connection pooling."""
    conn = await db_pool.get_connection()
    try:
        result = await conn.execute(sql)
        return result.fetchall()
    finally:
        await db_pool.return_connection(conn)
```

### Caching

```python
from functools import lru_cache
from fastmcp import FastMCP

mcp = FastMCP("agentx-cache")

@mcp.tool
@lru_cache(maxsize=128)
def cached_lookup(key: str) -> dict:
    """Cached lookup operation."""
    return expensive_lookup(key)

# Or with TTL cache
from cachetools import TTLCache

cache = TTLCache(maxsize=100, ttl=300)

@mcp.tool
def ttl_lookup(key: str) -> dict:
    """Lookup with 5-minute TTL."""
    if key in cache:
        return cache[key]

    result = expensive_lookup(key)
    cache[key] = result
    return result
```

### Async Optimization

```python
import asyncio
from fastmcp import FastMCP

mcp = FastMCP("agentx-async")

@mcp.tool
async def parallel_search(queries: list[str]) -> list[dict]:
    """Parallel search with asyncio."""
    tasks = [search(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results

@mcp.tool
async def batch_operation(items: list[str]) -> dict:
    """Batch processing with semaphore."""
    semaphore = asyncio.Semaphore(10)  # Max 10 concurrent

    async def process_item(item):
        async with semaphore:
            return await process(item)

    tasks = [process_item(item) for item in items]
    results = await asyncio.gather(*tasks)

    return {"processed": len(results), "results": results}
```

## Monitoring & Observability

### Custom Metrics

```python
from fastmcp import FastMCP
from prometheus_client import Counter, Histogram

# Define metrics
tool_calls = Counter(
    'mcp_tool_calls_total',
    'Total tool calls',
    ['tool_name', 'status']
)

tool_duration = Histogram(
    'mcp_tool_duration_seconds',
    'Tool execution duration',
    ['tool_name']
)

mcp = FastMCP("agentx-metrics")

@mcp.tool
async def measured_operation(data: str) -> str:
    """Operation with metrics collection."""
    tool_calls.labels('measured_operation', 'start').inc()

    with tool_duration.labels('measured_operation').time():
        try:
            result = await process(data)
            tool_calls.labels('measured_operation', 'success').inc()
            return result
        except Exception as e:
            tool_calls.labels('measured_operation', 'error').inc()
            raise
```

### Health Checks

```python
@mcp.tool(tags=["health"])
def health_check() -> dict:
    """Health check endpoint."""
    checks = {
        "database": check_db(),
        "redis": check_redis(),
        "storage": check_storage(),
    }

    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks
    }
```

## Security Best Practices

### Input Validation

```python
from pydantic import BaseModel, Field, validator

class SafeInput(BaseModel):
    data: str = Field(..., max_length=1000)

    @validator('data')
    def validate_data(cls, v):
        # Sanitize input
        if "<script>" in v.lower():
            raise ValueError("Potentially malicious input")
        return v

@mcp.tool
def safe_operation(input: SafeInput) -> dict:
    """Operation with validated input."""
    return process(input.data)
```

### Rate Limiting

```python
from fastmcp import FastMCP
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
mcp = FastMCP("agentx-ratelimit")

@mcp.tool
@limiter.limit("10/minute")
def rate_limited_operation(query: str) -> dict:
    """Operation with rate limiting."""
    return search(query)
```

### Authentication Middleware

```python
from fastmcp import FastMCP
from fastmcp.server.auth import AuthMiddleware

mcp = FastMCP("agentx-auth")

# Add authentication middleware
mcp.add_middleware(AuthMiddleware, providers=["github", "google"])

@mcp.tool
def protected_operation(data: str) -> dict:
    """Operation requiring authentication."""
    # Auth middleware verifies token before execution
    return process(data)
```

## AGENTX-Specific Implementation

### Company MIS Plugin

```python
# plugins/company_mis/server.py
from fastmcp import FastMCP
import httpx

mis_mcp = FastMCP("company-mis")

@mis_mcp.resource("metrics://revenue")
def get_revenue_metrics() -> str:
    """Current revenue metrics."""
    data = fetch_from_mis("revenue")
    return json.dumps({
        "current": data["current"],
        "target": data["target"],
        "variance": data["variance"],
        "trend": data["trend"]
    })

@mis_mcp.resource("alerts://active")
def get_active_alerts() -> str:
    """Active company alerts."""
    alerts = fetch_from_mis("alerts")
    return json.dumps([
        {
            "id": a["id"],
            "severity": a["severity"],
            "message": a["message"],
            "timestamp": a["created_at"]
        }
        for a in alerts if a["status"] == "active"
    ])

@mis_mcp.tool
def query_database(table: str, filters: dict) -> list[dict]:
    """Query company database.

    Args:
        table: Database table name
        filters: Filter criteria as key-value pairs

    Returns:
        List of matching records
    """
    return db.query(table, **filters)

if __name__ == "__main__":
    mis_mcp.run()
```

### SearXNG Search Plugin

```python
# plugins/searxng/server.py
from fastmcp import FastMCP
import httpx

search_mcp = FastMCP("searxng-search")

@search_mcp.tool
def web_search(query: str, categories: list[str] = None) -> list[dict]:
    """Search the web using SearXNG.

    Args:
        query: Search query string
        categories: Categories to search (default: all)

    Returns:
        List of search results with title, URL, snippet
    """
    if categories is None:
        categories = ["general", "science", "images"]

    response = httpx.get(
        "http://192.168.1.4:8080/search",
        params={
            "q": query,
            "categories": ",".join(categories),
            "format": "json"
        }
    )

    results = response.json()

    return [
        {
            "title": r["title"],
            "url": r["url"],
            "snippet": r["content"],
            "score": r["score"]
        }
        for r in results[:10]
    ]

@search_mcp.tool
def search_images(query: str, size: str = "medium") -> list[dict]:
    """Search for images using SearXNG.

    Args:
        query: Image search query
        size: Image size (small, medium, large, wall)

    Returns:
        List of image URLs with metadata
    """
    response = httpx.get(
        "http://192.168.1.4:8080/search",
        params={
            "q": query,
            "categories": "images",
            "img_size": size,
            "format": "json"
        }
    )

    results = response.json()

    return [
        {
            "url": r["img_src"],
            "title": r["title"],
            "source": r["engine"],
            "resolution": r.get("resolution", "unknown")
        }
        for r in results[:20]
    ]

if __name__ == "__main__":
    search_mcp.run()
```

### Vision Plugin

```python
# plugins/vision/server.py
from fastmcp import FastMCP
from PIL import Image
import base64

vision_mcp = FastMCP("agentx-vision")

@vision_mcp.tool
def analyze_image(image_path: str, task: str = "describe") -> dict:
    """Analyze image with vision model.

    Args:
        image_path: Path to image file
        task: Analysis task (describe, ocr, objects, faces)

    Returns:
        Analysis results based on task type
    """
    # Load and encode image
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode()

    # Call vision model via Ollama
    response = ollama_vision.generate(
        model="llava:latest",
        images=[image_data],
        prompt=f"{task} this image in detail"
    )

    return {
        "task": task,
        "image_path": image_path,
        "analysis": response
    }

@vision_mcp.tool
def detect_objects(image_path: str, confidence: float = 0.5) -> list[dict]:
    """Detect objects in image using YOLO.

    Args:
        image_path: Path to image file
        confidence: Detection confidence threshold (0-1)

    Returns:
        List of detected objects with bounding boxes
    """
    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")
    results = model(image_path, conf=confidence)

    detections = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append({
                "class": model.names[int(box.cls)],
                "confidence": float(box.conf),
                "bbox": [int(x1), int(y1), int(x2), int(y2)]
            })

    return detections

if __name__ == "__main__":
    vision_mcp.run()
```

## Development Workflow

### Local Development (RTX 3060)

```bash
# 1. Create virtual environment
uv venv .venv
source .venv/bin/activate

# 2. Install dependencies
uv pip install fastmcp mem0ai dspy qdrant-client fastembed

# 3. Run MCP server
python plugins/company_mis/server.py

# 4. Test with MCP Inspector
mcp dev plugins/company_mis/server.py

# 5. Connect from AGENTX core
# Agent will auto-discover tools from mounted servers
```

### Production (DGX Spark)

```bash
# 1. Scale to GPU cluster
kubectl scale deployment agentx-mcp --replicas=10

# 2. Deploy with GPU support
helm install agentx-mcp ./helm-chart \
  --set gpu.enabled=true \
  --set gpu.memory=500 \
  --set replicaCount=5

# 3. Load balance across instances
kubectl apply -f k8s/service.yaml

# 4. Monitor deployment
kubectl get pods -l app=agentx-mcp
kubectl logs -f deployment/agentx-mcp
```

## Configuration for Claude Desktop / Cursor

### Claude Desktop

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (Mac)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)
{
  "mcpServers": {
    "agentx-local": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/agentx",
        "run", "core/server.py"
      ],
      "env": {
        "OLLAMA_BASE_URL": "http://localhost:11434"
      }
    },
    "agentx-remote": {
      "url": "http://agentx-server:8080/api/mcp/",
      "headers": {
        "Authorization": "Bearer your-token"
      }
    }
  }
}
```

### Cursor / VS Code

```json
// .mcp.json or ~/.mcp.json
{
  "mcpServers": {
    "agentx": {
      "command": "python",
      "args": ["/path/to/agentx/core/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/agentx"
      }
    }
  }
}
```

## Troubleshooting

### Common Issues

**Issue 1: Server not discovered**

```bash
# Test MCP server manually
mcp dev server.py

# Check logs
tail -f logs/agentx-mcp.log

# Verify transport
curl http://localhost:8080/api/mcp/v1
```

**Issue 2: Tool not visible**

```python
# Add explicit tags
@mcp.tool(tags=["public"])
def my_tool(data: str) -> str:
    return data

# Check server configuration
mcp = FastMCP("agentx", include_tags={"public"})

# Verify with inspector
mcp dev server.py
```

**Issue 3: Authentication errors**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check token storage
mcp = FastMCP("agentx", auth_storage=storage)

# Verify OAuth flow
# Check browser console for OAuth errors
# Verify redirect URIs in OAuth provider
```

## Performance Benchmarks

### Expected Performance (RTX 3060)

| Operation | Latency | Throughput |
|-----------|---------|------------|
| **Tool call (simple)** | 50-100ms | ~100 calls/sec |
| **Tool call (with LLM)** | 2-5s | ~5 calls/sec |
| **Resource access** | 10-50ms | ~200 calls/sec |
| **Server startup** | 1-2s | - |

### Expected Performance (DGX Spark)

| Operation | Latency | Throughput |
|-----------|---------|------------|
| **Tool call (simple)** | 10-30ms | ~1000 calls/sec |
| **Tool call (with LLM)** | 500ms-2s | ~50 calls/sec |
| **Resource access** | 5-20ms | ~500 calls/sec |
| **Server startup** | 500ms-1s | - |

## Next Steps

1. **Set up development environment**
   ```bash
   uv venv .venv
   source .venv/bin/activate
   uv pip install fastmcp[cli,dev]
   ```

2. **Create first MCP server**
   ```bash
   mkdir -p plugins/company_mis
   touch plugins/company_mis/server.py
   ```

3. **Test with MCP Inspector**
   ```bash
   mcp dev plugins/company_mis/server.py
   ```

4. **Integrate with AGENTX core**
   - Mount servers in main AGENTX server
   - Configure DSPy to use MCP tools
   - Test end-to-end workflows

5. **Deploy to production**
   - Containerize with Docker
   - Deploy to DGX Spark
   - Set up monitoring and observability

## References

- [FastMCP Official Docs](https://gofastmcp.com)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [FastMCP Changelog](https://gofastmcp.com/changelog)
- [Prefect (Creator)](https://prefect.io/)

## Summary

FastMCP 2.0 is the **recommended framework** for building AGENTX plugins because:

✅ **Enterprise-ready authentication** (OAuth, JWT, API keys)
✅ **Advanced composition** (mounting, importing, proxying)
✅ **FastAPI integration** (one-line conversion)
✅ **Production deployment** (Docker, K8s, FastMCP Cloud)
✅ **Developer experience** (decorators, type hints, testing)
✅ **Scalability** (connection pooling, async, caching)
✅ **Monitoring** (metrics, logging, health checks)

**For your JARVIS vision:**
- Use FastMCP for all AGENTX plugins
- Leverage server composition for modular architecture
- Deploy each plugin as separate MCP server
- Use FastMCP's built-in auth for enterprise security
- Scale horizontally on DGX Spark

The plugin architecture is ready - now build the multimodal brain! 🚀
