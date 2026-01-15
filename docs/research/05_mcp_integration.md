# Model Context Protocol (MCP) Integration Guide

## Overview

Model Context Protocol (MCP) is an open standard that enables AI agents to communicate with external tools, data sources, and systems. AGENTX uses MCP for plugin extensibility, particularly for Company MIS integration.

## What is MCP?

### Core Concept

MCP standardizes how AI assistants connect to:
- **Tools** - Executable functions and APIs
- **Resources** - Data sources and files
- **Prompts** - Reusable prompt templates

### Benefits

- **Universal integration** - Single protocol for all tools
- **Plug-and-play** - Dynamic tool discovery
- **Standardized communication** - Consistent interface
- **Multi-vendor support** - Anthropic, OpenAI, Google, Microsoft

## Architecture

### MCP Components

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   AI Agent  │────▶│  MCP Host   │────▶│  MCP Server │
│  (Client)   │     │  (AGENTX)   │     │   (Plugin)  │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                    ┌───────┴────────┐
                    ▼                ▼
              ┌──────────┐    ┌──────────┐
              │   Tool   │    │ Resource │
              │ Registry │    │ Provider │
              └──────────┘    └──────────┘
```

### Transport Layers

- **STDIO** - Local process communication
- **SSE** - Server-Sent Events over HTTP
- **HTTP** - REST-style API calls
- **gRPC** - High-performance RPC (coming)

## Implementation

### 1. MCP Server for Company MIS

```python
# plugins/company_mis/mcp_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

app = Server("agentx-company-mis")

# Define tools
@app.tool(
    name="get_company_data",
    description="Retrieve company financial and operational data"
)
async def get_company_data(
    metric: str,
    period: str = "current_month"
) -> str:
    """Get company MIS data."""
    # Query company database
    data = await query_company_mis(metric, period)

    return json.dumps({
        "metric": metric,
        "period": period,
        "value": data["value"],
        "change": data.get("change", 0),
        "timestamp": data["timestamp"]
    })


@app.tool(
    name="list_alerts",
    description="Get active company alerts and warnings"
)
async def list_alerts(
    severity: str = None,
    category: str = None
) -> str:
    """List company alerts."""
    alerts = await get_company_alerts(severity, category)

    return json.dumps({
        "count": len(alerts),
        "alerts": [
            {
                "id": a["id"],
                "severity": a["severity"],
                "message": a["message"],
                "created_at": a["created_at"]
            }
            for a in alerts
        ]
    })


@app.tool(
    name="create_alert",
    description="Create a new company alert"
)
async def create_alert(
    message: str,
    severity: str = "info",
    category: str = "general"
) -> str:
    """Create company alert."""
    alert_id = await insert_company_alert(
        message=message,
        severity=severity,
        category=category
    )

    return json.dumps({
        "success": True,
        "alert_id": alert_id
    })


# Resources
@app.resource("uri://company/metrics/{metric}")
async def get_metric_resource(metric: str) -> str:
    """Get metric as resource."""
    data = await get_company_data(metric, "current_month")
    return json.dumps(json.loads(data), indent=2)


@app.resource("uri://company/alerts")
async def get_alerts_resource() -> str:
    """Get all alerts as resource."""
    alerts = await list_alerts()
    return json.dumps(json.loads(alerts), indent=2)


# Start server
if __name__ == "__main__":
    app.run(transport="stdio")
```

### 2. MCP Host Integration

```python
# core/mcp_host.py
from mcp.client import ClientSession, StdioServerParameters
from typing import Dict, List, Any

class MCPHost:
    """MCP host for managing MCP server connections."""

    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}

    async def connect_server(
        self,
        name: str,
        command: str,
        args: List[str] = None
    ) -> ClientSession:
        """Connect to an MCP server."""
        server_params = StdioServerParameters(
            command=command,
            args=args or []
        )

        session = ClientSession(server_params)
        await session.initialize()

        self.sessions[name] = session
        return session

    async def get_tools(self, server_name: str) -> List[Tool]:
        """Get available tools from server."""
        session = self.sessions.get(server_name)
        if not session:
            return []

        response = await session.list_tools()
        return response.tools

    async def call_tool(
        self,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """Call a tool on MCP server."""
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")

        result = await session.call_tool(tool_name, arguments)
        return result

    async def get_resource(
        self,
        server_name: str,
        uri: str
    ) -> str:
        """Get resource from MCP server."""
        session = self.sessions.get(server_name)
        if not session:
            raise ValueError(f"Server {server_name} not connected")

        result = await session.read_resource(uri)
        return result
```

### 3. DSPy Integration

```python
# core/mcp_tools.py
import dspy

class MCPTool(dspy.Tool):
    """DSPy tool wrapper for MCP tools."""

    def __init__(
        self,
        mcp_host: MCPHost,
        server_name: str,
        tool_name: str
    ):
        self.mcp_host = mcp_host
        self.server_name = server_name
        self.tool_name = tool_name

        # Get tool info
        tools = mcp_host.get_tools(server_name)
        self.tool_info = next(
            (t for t in tools if t.name == tool_name),
            None
        )

    def __call__(self, **kwargs):
        """Execute MCP tool."""
        import asyncio

        result = asyncio.run(
            self.mcp_host.call_tool(
                self.server_name,
                self.tool_name,
                kwargs
            )
        )

        return result


# Usage in DSPy agent
class MISAwareAgent(dspy.Module):
    """Agent with MCP tool access."""

    def __init__(self, mcp_host: MCPHost):
        super().__init__()

        # Wrap MCP tools as DSPy tools
        self.get_company_data = MCPTool(
            mcp_host,
            "company_mis",
            "get_company_data"
        )

        self.list_alerts = MCPTool(
            mcp_host,
            "company_mis",
            "list_alerts"
        )

        # Create ReAct agent
        self.react = dspy.ReAct(
            "question -> answer",
            tools=[self.get_company_data, self.list_alerts]
        )

    def forward(self, question: str):
        """Process question with MCP tools."""
        return self.react(question=question)
```

## Configuration

### Server Configuration

```yaml
# config/mcp_servers.yaml
mcp_servers:
  company_mis:
    enabled: true
    command: "python"
    args:
      - "-m"
      - "plugins.company_mis.mcp_server"
    env:
      DATABASE_URL: "postgresql://localhost/company_db"

  web_search:
    enabled: true
    command: "npx"
    args:
      - "-y"
      - "@modelcontextprotocol/server-brave-search"

  filesystem:
    enabled: false
    command: "npx"
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/home/riju279/Documents"
```

### Host Initialization

```python
# core/agentx.py
import yaml
from core.mcp_host import MCPHost

async def initialize_mcp(
    config_path: str = "config/mcp_servers.yaml"
) -> MCPHost:
    """Initialize MCP host with configured servers."""
    with open(config_path) as f:
        config = yaml.safe_load(f)

    host = MCPHost()

    for server_name, server_config in config["mcp_servers"].items():
        if not server_config.get("enabled", False):
            continue

        try:
            await host.connect_server(
                name=server_name,
                command=server_config["command"],
                args=server_config.get("args", [])
            )

            # Set environment variables
            for key, value in server_config.get("env", {}).items():
                import os
                os.environ[key] = value

            print(f"✓ Connected MCP server: {server_name}")

        except Exception as e:
            print(f"✗ Failed to connect {server_name}: {e}")

    return host
```

## Use Cases

### 1. Company Dashboard Query

```python
# Query: "What's our current revenue and any alerts?"

agent = MISAwareAgent(mcp_host)
response = agent("What's our current revenue and any alerts?")

# Agent will:
# 1. Call get_company_data("revenue")
# 2. Call list_alerts()
# 3. Synthesize response
```

### 2. Automated Alert Monitoring

```python
async def monitor_alerts():
    """Monitor and respond to alerts."""
    while True:
        # Get critical alerts
        alerts = await mcp_host.call_tool(
            "company_mis",
            "list_alerts",
            {"severity": "critical"}
        )

        # Process each alert
        for alert in alerts["alerts"]:
            await handle_alert(alert)

        # Wait before next check
        await asyncio.sleep(300)  # 5 minutes
```

### 3. Data Analysis

```python
# Query: "Compare revenue vs expenses for last 3 months"

response = agent("""
Compare revenue vs expenses for the last 3 months.
For each month, calculate the profit margin.
""")

# Agent will:
# 1. Call get_company_data("revenue", "month_1")
# 2. Call get_company_data("expenses", "month_1")
# 3. Repeat for months 2 and 3
# 4. Calculate and summarize
```

## Security

### 1. Sandboxing

```python
# Run MCP servers in isolated environments
server_config = {
    "command": "docker",
    "args": [
        "run",
        "--rm",
        "--network=none",  # No network access
        "-v", "/data:/data:ro",  # Read-only mount
        "company-mis-server"
    ]
}
```

### 2. Authentication

```python
# Add auth to MCP tools
@app.tool(name="sensitive_operation")
async def sensitive_operation(
    user_id: str,
    token: str,
    operation: str
) -> str:
    """Protected operation requiring auth."""
    # Verify token
    if not verify_token(user_id, token):
        raise UnauthorizedError()

    # Execute operation
    return await execute_operation(operation)
```

### 3. Rate Limiting

```python
from functools import wraps
import time

def rate_limit(calls_per_second: float):
    """Rate limiter decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            elapsed = now - last_called[0]

            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            last_called[0] = time.time()
            return await func(*args, **kwargs)

        return wrapper
    return decorator


@app.tool(name="rate_limited_query")
@rate_limit(calls_per_second=10)
async def rate_limited_query(query: str) -> str:
    """Rate-limited query."""
    return await execute_query(query)
```

## Best Practices

### 1. Error Handling

```python
async def safe_tool_call(
    server_name: str,
    tool_name: str,
    **kwargs
) -> dict:
    """Safe tool call with error handling."""
    try:
        result = await mcp_host.call_tool(
            server_name,
            tool_name,
            kwargs
        )
        return {"success": True, "data": result}

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "server": server_name,
            "tool": tool_name
        }
```

### 2. Tool Discovery

```python
async def discover_all_tools(mcp_host: MCPHost) -> Dict[str, List[Tool]]:
    """Discover all available tools."""
    all_tools = {}

    for server_name in mcp_host.sessions.keys():
        tools = await mcp_host.get_tools(server_name)
        all_tools[server_name] = tools

    return all_tools


# Usage
tools = await discover_all_tools(mcp_host)
for server, server_tools in tools.items():
    print(f"\n{server}:")
    for tool in server_tools:
        print(f"  - {tool.name}: {tool.description}")
```

### 3. Resource Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
async def get_cached_resource(
    server_name: str,
    uri: str,
    ttl: int = 60
) -> str:
    """Get resource with caching."""
    return await mcp_host.get_resource(server_name, uri)
```

## References

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Anthropic MCP SDK](https://github.com/anthropics/anthropic-sdk-python)
- [MCP Server Directory](https://github.com/modelcontextprotocol/servers)
- [MCP in JetBrains](https://www.jetbrains.com/help/ai-assistant/mcp.html)
