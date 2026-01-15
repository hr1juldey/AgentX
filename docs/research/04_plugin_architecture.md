# Plugin Architecture for AGENTX

## Overview

AGENTX uses a core + plugin architecture where the core provides essential memory-enabled chat functionality, and plugins extend capabilities like web search, company MIS integration, personality systems, TTS/STT, and computer vision.

## Architecture Principles

### 1. Separation of Concerns
- **Core**: Memory, chat, reasoning
- **Plugins**: Specialized capabilities
- **Interface**: Standardized plugin API

### 2. Dynamic Loading
- Hot-swappable plugins
- No system restart required
- Runtime capability discovery

### 3. Isolation
- Plugin failures don't crash core
- Resource quotas per plugin
- Independent lifecycle management

## Core System

### Minimal Core Components

```python
# core/agent.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import dspy
from mem0 import Memory

class PluginInterface(ABC):
    """Base interface for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        pass

    @property
    def dependencies(self) -> List[str]:
        """Required plugins."""
        return []

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """Execute plugin functionality."""
        pass

    def shutdown(self) -> None:
        """Cleanup resources."""
        pass


class AgentXCore:
    """Core agent with memory and plugin management."""

    def __init__(self, config: Dict[str, Any]):
        # Initialize DSPy
        lm = dspy.LM(
            model=config.get("model", "ollama/llama3.2"),
            api_base=config.get("api_base", "http://localhost:11434")
        )
        dspy.configure(lm=lm)

        # Initialize Memory
        self.memory = Memory.from_config(config["memory"])

        # Plugin registry
        self.plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, Dict] = config.get("plugins", {})

        # Load plugins
        self._load_plugins()

    def _load_plugins(self):
        """Load configured plugins."""
        import importlib

        for plugin_name, plugin_config in self.plugin_configs.items():
            try:
                module_path = f"plugins.{plugin_name}"
                module = importlib.import_module(module_path)

                plugin_class = getattr(module, f"{plugin_name.title()}Plugin")
                plugin = plugin_class()

                # Check dependencies
                deps_met = all(
                    dep in self.plugins
                    for dep in plugin.dependencies
                )

                if deps_met:
                    plugin.initialize(plugin_config)
                    self.plugins[plugin.name] = plugin
                    print(f"✓ Loaded plugin: {plugin.name} v{plugin.version}")
                else:
                    print(f"✗ Plugin {plugin.name} missing dependencies")

            except Exception as e:
                print(f"✗ Failed to load {plugin_name}: {e}")

    def chat(self, message: str, user_id: str = "default") -> str:
        """Process chat message with all plugins."""
        # Search memory
        context = self._search_memory(message, user_id)

        # Execute plugins
        plugin_results = {}
        for name, plugin in self.plugins.items():
            try:
                result = plugin.execute(
                    message=message,
                    context=context,
                    user_id=user_id
                )
                plugin_results[name] = result
            except Exception as e:
                print(f"Plugin {name} error: {e}")
                plugin_results[name] = None

        # Generate response
        response = self._generate_response(
            message=message,
            context=context,
            plugin_data=plugin_results
        )

        # Store in memory
        self.memory.add(
            f"User: {message}\nAgent: {response}",
            user_id=user_id
        )

        return response

    def _search_memory(self, query: str, user_id: str) -> str:
        """Search for relevant memories."""
        results = self.memory.search(query, user_id=user_id, limit=3)
        memories = results.get("results", [])
        return "\n".join([m["memory"] for m in memories])

    def _generate_response(
        self,
        message: str,
        context: str,
        plugin_data: Dict[str, Any]
    ) -> str:
        """Generate response using DSPy."""
        class ChatSignature(dspy.Signature):
            """Chat response generation."""
            user_input: str = dspy.InputField()
            context: str = dspy.InputField()
            plugin_data: str = dspy.InputField()
            response: str = dspy.OutputField()

        chat = dspy.Predict(ChatSignature)
        result = chat(
            user_input=message,
            context=context,
            plugin_data=str(plugin_data)
        )

        return result.response
```

## Plugin Examples

### 1. Web Search Plugin (SearXNG)

```python
# plugins/web_search.py
import requests
from typing import Any, Dict

class WebSearchPlugin(PluginInterface):
    """SearXNG web search integration."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        self.searxng_url = config.get(
            "searxng_url",
            "http://192.168.1.4:8080"
        )
        self.max_results = config.get("max_results", 5)

    def execute(self, message: str, **kwargs) -> Dict[str, Any]:
        """Search the web for relevant information."""
        try:
            # Extract query from message
            query = self._extract_query(message)

            # Search SearXNG
            params = {
                "q": query,
                "format": "json",
                "engines": "google,bing,duckduckgo"
            }

            response = requests.get(
                f"{self.searxng_url}/search",
                params=params,
                timeout=10
            )

            results = response.json()

            # Format results
            formatted = {
                "query": query,
                "results": [
                    {
                        "title": r.get("title"),
                        "url": r.get("url"),
                        "snippet": r.get("content")
                    }
                    for r in results.get("results", [])[:self.max_results]
                ],
                "count": len(results.get("results", []))
            }

            return formatted

        except Exception as e:
            return {"error": str(e), "results": []}

    def _extract_query(self, message: str) -> str:
        """Extract search query from message."""
        # Simple keyword extraction
        keywords = ["search for", "find", "look up", "google"]
        message_lower = message.lower()

        for keyword in keywords:
            if keyword in message_lower:
                return message.split(keyword, 1)[1].strip()

        return message
```

### 2. TTS Plugin

```python
# plugins/tts.py
import io
from pydub import AudioSegment
from pydub.playback import play

class TTSPlugin(PluginInterface):
    """Text-to-Speech plugin using Piper."""

    @property
    def name(self) -> str:
        return "tts"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        self.voice = config.get("voice", "en-us-amy-low")
        self.speed = config.get("speed", 1.0)

    def execute(self, message: str, **kwargs) -> Dict[str, Any]:
        """Convert text to speech."""
        try:
            # Call Piper TTS
            import requests

            response = requests.post(
                "http://localhost:8080/generate",
                json={
                    "text": kwargs.get("response", message),
                    "voice": self.voice,
                    "speed": self.speed
                },
                timeout=30
            )

            if response.status_code == 200:
                audio_data = response.content

                # Play audio
                audio = AudioSegment.from_file(
                    io.BytesIO(audio_data),
                    format="wav"
                )
                play(audio)

                return {"success": True}
            else:
                return {"error": "TTS generation failed"}

        except Exception as e:
            return {"error": str(e)}
```

### 3. Computer Vision Plugin

```python
# plugins/vision.py
import base64
from typing import Any, Dict

class VisionPlugin(PluginInterface):
    """Computer vision plugin for image analysis."""

    @property
    def name(self) -> str:
        return "vision"

    @property
    def version(self) -> str:
        return "1.0.0"

    def initialize(self, config: Dict[str, Any]) -> None:
        self.model = config.get("model", "ollama/llava")
        self.api_base = config.get(
            "api_base",
            "http://localhost:11434"
        )

    def execute(self, image_path: str, prompt: str = "", **kwargs) -> Dict[str, Any]:
        """Analyze image with vision model."""
        try:
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()

            # Call vision model
            import dspy

            vision_lm = dspy.LM(
                model=self.model,
                api_base=self.api_base
            )

            response = vision_lm(
                images=[image_data],
                prompt=prompt or "Describe this image in detail."
            )

            return {
                "description": response,
                "image_path": image_path
            }

        except Exception as e:
            return {"error": str(e)}
```

## Plugin Discovery

### Capability Registration

```python
# plugins/base.py
from typing import Set, Dict

class PluginCapabilities:
    """Registry for plugin capabilities."""

    def __init__(self):
        self.capabilities: Dict[str, Set[str]] = {}

    def register(self, plugin_name: str, capabilities: Set[str]):
        """Register plugin capabilities."""
        self.capabilities[plugin_name] = capabilities

    def discover(self, required: Set[str]) -> List[str]:
        """Find plugins that provide required capabilities."""
        matching = []

        for plugin, caps in self.capabilities.items():
            if required.issubset(caps):
                matching.append(plugin)

        return matching


# Example usage
capabilities = PluginCapabilities()

capabilities.register("web_search", {"search", "web", "information"})
capabilities.register("vision", {"image", "analysis", "visual"})
capabilities.register("tts", {"audio", "speech", "output"})

# Find plugins for specific needs
plugins = capabilities.discover({"search", "web"})
# Returns: ["web_search"]
```

### Runtime Plugin Loading

```python
# core/plugin_loader.py
import importlib
import inspect
from pathlib import Path

class PluginLoader:
    """Dynamic plugin loader."""

    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.loaded_plugins: Dict[str, PluginInterface] = {}

    def discover_plugins(self) -> List[PluginInterface]:
        """Discover all available plugins."""
        plugins = []

        for plugin_file in self.plugin_dir.glob("*/plugin.py"):
            module_path = plugin_file.parent.name

            try:
                module = importlib.import_module(
                    f"plugins.{module_path}.plugin"
                )

                # Find plugin class
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, PluginInterface) and
                        obj != PluginInterface):

                        plugins.append(obj)

            except Exception as e:
                print(f"Failed to load {module_path}: {e}")

        return plugins

    def load_plugin(
        self,
        plugin_class: type[PluginInterface],
        config: Dict
    ) -> PluginInterface:
        """Load and initialize a plugin."""
        plugin = plugin_class()
        plugin.initialize(config)

        self.loaded_plugins[plugin.name] = plugin
        return plugin
```

## Configuration

### Plugin Config File

```yaml
# config/plugins.yaml
plugins:
  web_search:
    enabled: true
    searxng_url: "http://192.168.1.4:8080"
    max_results: 5

  tts:
    enabled: true
    voice: "en-us-amy-low"
    speed: 1.0

  vision:
    enabled: true
    model: "ollama/llava"
    api_base: "http://localhost:11434"

  company_mis:
    enabled: false
    mcp_server: "http://localhost:8000"

  personality:
    enabled: true
    active_profile: "professional"
```

### Loading Configuration

```python
import yaml

def load_plugin_config(config_path: str = "config/plugins.yaml"):
    """Load plugin configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)

# Initialize agent with plugins
config = load_plugin_config()

agent = AgentXCore({
    "model": "ollama/llama3.2",
    "memory": {...},
    "plugins": config["plugins"]
})
```

## Best Practices

### 1. Plugin Communication

```python
# Plugins can communicate via events
class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, event: str, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append(callback)

    def publish(self, event: str, data):
        for callback in self.listeners.get(event, []):
            callback(data)

# Usage in plugin
def initialize(self, config):
    event_bus = config.get("event_bus")
    event_bus.subscribe("message", self.on_message)
```

### 2. Error Isolation

```python
def execute(self, **kwargs):
    """Execute with error isolation."""
    try:
        return self._do_execute(**kwargs)
    except Exception as e:
        # Log error
        print(f"{self.name} error: {e}")

        # Return error result
        return {
            "plugin": self.name,
            "error": str(e),
            "success": False
        }
```

### 3. Resource Cleanup

```python
def shutdown(self):
    """Cleanup plugin resources."""
    # Close connections
    if hasattr(self, 'session'):
        self.session.close()

    # Release resources
    if hasattr(self, 'model'):
        del self.model

    # Unregister
    self._unregister()
```

## References

- [DSPy Tools](https://dspy.ai/api/tools/)
- [Python Plugin Architecture](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
- [Semantic Kernel Plugins](https://learn.microsoft.com/en-us/semantic-kernel/concepts-sk/plugins)
