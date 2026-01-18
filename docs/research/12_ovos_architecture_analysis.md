# OVOS Architecture Analysis: Core vs Plugin Design

**Version**: 1.0.0
**Date**: 2026-01-18
**Purpose**: Comprehensive analysis of OpenVoiceOS (OVOS) architecture to inform AGENTX plugin system design

---

## Executive Summary

This document analyzes the OpenVoiceOS (OVOS) architecture, focusing on the separation between core and plugin components, plugin template architecture, and loose coupling strategies. Key findings include:

- **Plugin-based architecture** using Python entrypoints for discovery
- **Abstract base classes** defining plugin interfaces via ovos-plugin-manager (OPM)
- **Message bus** as communication backbone for loose coupling
- **Configuration-driven** loading via mycroft.conf
- **Portable plugins** that work independently of the core system

---

## 1. Core vs Plugin Separation

### 1.1 What Belongs in Core

The **ovos-core** repository contains essential system infrastructure:

| Component | Purpose | Location |
|-----------|---------|----------|
| **Intent Services** | Intent matching and handling | `intent_services/` |
| **Skill Manager** | Skill lifecycle management | `skill_manager.py` |
| **Skill Installer** | Skill installation/update logic | `skill_installer.py` |
| **Transformers** | Audio/text transformation pipeline | `transformers.py` |
| **Message Bus** | Inter-component communication | Core infrastructure |
| **Configuration System** | mycroft.conf management | Core infrastructure |

**Core Responsibilities**:
```python
# From skill_manager.py - Core manages plugin lifecycle
class SkillManager(Thread):
    """Manages the loading, activation, and deactivation of skills."""

    def __init__(self, bus, watchdog=None, ...):
        super(SkillManager, self).__init__()
        self.bus = bus  # Message bus for loose coupling
        self.plugin_skills = {}
        self.intents = IntentService(self.bus)

    def load_plugin_skills(self, network=None, internet=None):
        """Load plugin skills based on network/internet status."""
        plugins = find_skill_plugins()
        for skill_id, plug in plugins.items():
            if skill_id in self.blacklist:
                continue
            # Network-aware skill loading
```

**Design Principle**: Core provides orchestration, infrastructure, and communication. Core knows *about* plugins but not *how* they work internally.

### 1.2 What Belongs in Plugins

**All domain-specific functionality** should be plugins:

| Plugin Type | Entrypoint | Purpose |
|-------------|------------|---------|
| **STT** | `mycroft.plugin.stt` | Speech-to-Text engines |
| **TTS** | `mycroft.plugin.tts` | Text-to-Speech engines |
| **Wake Word** | `mycroft.plugin.wake_word` | Hotword detection |
| **VAD** | `ovos.plugin.VAD` | Voice Activity Detection |
| **Audio** | `mycroft.plugin.audioservice` | Audio playback services |
| **Skill** | `ovos.plugin.skill` | Intent-based capabilities |
| **PHAL** | `ovos.plugin.phal` | Platform Hardware Abstraction Layer |
| **GUI** | `ovos.plugin.gui` | Graphical interface plugins |
| **G2P** | `ovos.plugin.g2p` | Grapheme-to-Phoneme conversion |
| **Translate** | `neon.plugin.lang.translate` | Language translation |
| **Solvers** | `neon.plugin.solver` | Question answering |
| **Transformers** | `neon.plugin.{audio|text|metadata}` | Data transformation |

**Complete PluginTypes Enum**:
```python
class PluginTypes(str, Enum):
    # Platform Hardware Abstraction Layer
    PHAL = "ovos.plugin.phal"
    ADMIN = "ovos.plugin.phal.admin"

    # AI/Capabilities
    SKILL = "ovos.plugin.skill"
    VAD = "ovos.plugin.VAD"
    PHONEME = "ovos.plugin.g2p"

    # Audio Pipeline
    AUDIO = 'mycroft.plugin.audioservice'
    STT = 'mycroft.plugin.stt'
    TTS = 'mycroft.plugin.tts'
    WAKEWORD = 'mycroft.plugin.wake_word'

    # Language
    TRANSLATE = "neon.plugin.lang.translate"
    LANG_DETECT = "neon.plugin.lang.detect"

    # Transformers
    UTTERANCE_TRANSFORMER = "neon.plugin.text"
    METADATA_TRANSFORMER = "neon.plugin.metadata"
    AUDIO_TRANSFORMER = "neon.plugin.audio"

    # Question Answering
    QUESTION_SOLVER = "neon.plugin.solver"

    # And more...
```

**Design Principle**: Plugins encapsulate specific capabilities and can be developed, tested, and distributed independently of the core.

---

## 2. Core Architecture

### 2.1 Communication Backbone: Message Bus

The **message bus** is the primary loose coupling mechanism:

```python
# Core sends messages without knowing which plugins receive them
bus.emit(Message("recognizer_loop:utterance", {
    "utterances": ["turn on the lights"],
    "lang": "en-us"
}))

# Plugins subscribe to messages they care about
@intent_handler("TurnOnLightsIntent")
def handle_turn_on_lights(self, message):
    # Handle the intent
```

**Benefits**:
- Zero direct dependencies between components
- Runtime discovery of capabilities
- Easy to add/remove plugins without code changes
- Natural support for distributed systems

### 2.2 Plugin Discovery: Entrypoints

**Python packaging entrypoints** enable plugin discovery:

```python
# In plugin's setup.py
PLUGIN_TYPE = "mycroft.plugin.stt"
PLUGIN_NAME = "ovos-stt-plugin-name"
PLUGIN_PKG = PLUGIN_NAME.replace("-", "_")
PLUGIN_CLAZZ = "MySTT"

setup(
    name=PLUGIN_NAME,
    entry_points={
        PLUGIN_TYPE: f'{PLUGIN_NAME} = {PLUGIN_PKG}:{PLUGIN_CLAZZ}',
        f'{PLUGIN_TYPE}.config': f'{PLUGIN_NAME}.config = {PLUGIN_PKG}:get_config'
    }
)
```

**Core discovers plugins at runtime**:
```python
import pkg_resources

# Find all STT plugins
for entry_point in pkg_resources.iter_entry_points('mycroft.plugin.stt'):
    plugin_class = entry_point.load()
    plugin_instance = plugin_class(config)
```

### 2.3 Configuration System: mycroft.conf

**Declarative plugin selection** via configuration:

```json
{
  "stt": {
    "module": "ovos-stt-plugin-server",
    "ovos-stt-plugin-server": {
      "url": "https://stt.example.com"
    }
  },
  "tts": {
    "module": "ovos-tts-plugin-silero",
    "ovos-tts-plugin-silero": {
      "model": "v3_en",
      "speaker": "en_5"
    }
  }
}
```

**Benefits**:
- No code changes to swap plugins
- User-configurable system behavior
- Easy A/B testing of implementations
- Configuration validation at startup

---

## 3. Plugin Template Architecture

### 3.1 Abstract Base Classes (ABC)

OPM provides **abstract base classes** for each plugin type:

#### STT Plugin Template

```python
from abc import ABCMeta, abstractmethod
from typing import Optional, Set

class STT(metaclass=ABCMeta):
    """STT Base class - all STT backends derive from this one."""

    def __init__(self, config=None):
        self.config_core = Configuration()
        self._lang = None
        self._credential = None
        self._keys = None
        self.config = config or {}
        self.can_stream = False

    @abstractmethod
    def execute(self, audio: AudioData, language: Optional[str] = None) -> str:
        """Transcribe the provided audio and return the best-matching text."""
        pass

    @classproperty
    @abstractmethod
    def available_languages(cls) -> Set[str]:
        """Return languages supported by this STT implementation."""
        pass
```

**Key Pattern**: Abstract methods define the **required interface**. Plugin authors implement only these methods.

#### TTS Plugin Template

```python
class TTS:
    """TTS abstract class to be implemented by all TTS engines."""

    queue = None
    playback = None

    def __init__(self, config=None, validator=None,
                 audio_ext='wav', phonetic_spelling=True, ssml_tags=None):
        self.config = config or {}
        self.validator = validator or TTSValidator(self)
        self.phonetic_spelling = phonetic_spelling
        self.audio_ext = audio_ext
        self.ssml_tags = ssml_tags or []
        self.enable_cache = self.config.get("enable_cache", True)

    @abstractmethod
    def get_tts(self, phrase, language):
        """Generate audio from text and return (audio_data, phonemes)."""
        pass

    def validate(self, connection):
        """Validate connection to TTS engine."""
        return self.validator.validate(connection)
```

**Key Patterns**:
- Optional hooks (`validate`) with default implementations
- Built-in caching support via `TTSContext`
- SSML and phonetic spelling as standard features

### 3.2 Plugin Implementation Example

```python
from ovos_plugin_manager.templates import TTS

class SileroTTS(TTS):
    """Silero TTS plugin implementation."""

    def __init__(self, config=None):
        super().__init__(config, audio_ext='wav')
        self.model = self._load_model()

    def get_tts(self, phrase, language):
        """Generate speech using Silero model."""
        audio = self.model.apply_tts(
            text=phrase,
            speaker=self.config.get("speaker", "en_5"),
            sample_rate=24000
        )
        return audio.cpu().numpy(), None

    @property
    def available_languages(self):
        return {"en-us", "en-gb"}
```

**Key Insight**: Plugin authors only implement domain-specific logic. All infrastructure (loading, validation, caching) is inherited.

---

## 4. Loose Coupling Strategies

### 4.1 Message Bus Pattern

**Indirect communication** via typed messages:

```python
# Component A: Send without knowing receivers
bus.emit(Message("speak", {"utterance": "Hello world"}))

# Component B: Receive without knowing sender
bus.on("speak", self.handle_speak)

def handle_speak(self, message):
    utterance = message.data.get("utterance")
    self.tts.synthesize(utterance)
```

**Benefits**:
- Zero compile-time dependencies
- Runtime discovery and binding
- Easy to mock for testing
- Supports distributed deployment

### 4.2 Configuration-Based Binding

**Declarative wiring** via configuration files:

```json
{
  "skills": {
    "auto_update": true,
    "priority_skills": ["mycroft-media", "mycroft-date-time"],
    "blacklist": ["skill-dont-use"]
  }
}
```

**Benefits**:
- No code changes to reconfigure
- Different configurations per environment
- User-customizable behavior
- Easy rollback via configuration

### 4.3 Abstract Interface Contracts

**ABCs enforce API contracts** at the type level:

```python
from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def process(self, input_data: dict) -> dict:
        """Process input and return output."""
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if plugin dependencies are met."""
        pass
```

**Benefits**:
- Compile-time verification of plugin compliance
- Clear documentation via type signatures
- IDE autocomplete support
- Fail-fast on missing implementations

### 4.4 Entrypoint-Based Discovery

**Runtime plugin loading** without imports:

```python
# No imports needed - plugins discovered at runtime
import pkg_resources

plugins = []
for entry_point in pkg_resources.iter_entry_points('my.plugin.type'):
    plugin_class = entry_point.load()
    if plugin_class.is_available():
        plugins.append(plugin_class())
```

**Benefits**:
- Optional dependencies (plugins not required)
- Dynamic loading based on environment
- No circular import issues
- Easy to add plugins without modifying core

### 4.5 Dependency Injection

**Constructor injection** of dependencies:

```python
class MyPlugin:
    def __init__(self, bus, config):
        self.bus = bus  # Inject message bus
        self.config = config  # Inject configuration
        # Optional: Inject other dependencies
        self.tts = self._get_dependency("tts", bus)
```

**Benefits**:
- Explicit dependencies
- Easy to mock for testing
- Supports multiple implementations
- Clear dependency graph

---

## 5. Plugin Portability

### 5.1 Standalone Plugin Usage

Plugins work **independently of the core**:

```python
# Use STT plugin directly, without OVOS core
from ovos_plugin_manager.stt import SileroSTT

stt = SileroSTT(config={"model": "v3_en"})
with open("audio.wav", "rb") as f:
    text = stt.execute(f.read(), language="en")
print(text)
```

**Design Implication**: Plugin base classes should not depend on core infrastructure.

### 5.2 Plugin Versioning

**Semantic versioning** for plugins:

```python
# setup.py
setup(
    name="my-stt-plugin",
    version="1.2.3",
    install_requires=[
        "ovos-plugin-manager>=0.0.1,<1.0.0"  # API compatibility
    ]
)
```

**Benefits**:
- Clear API contracts between versions
- Graceful deprecation warnings
- Multiple plugin versions coexist

---

## 6. Lessons for AGENTX Design

### 6.1 Apply to AGENTX Plugin System

| OVOS Pattern | AGENTX Application |
|--------------|-------------------|
| Message bus | FastMCP + event bus |
| Entrypoints | FastMCP server discovery |
| ABC templates | Abstract base classes for tool types |
| mycroft.conf | AGENTX config.yaml |
| OPM | `agentx_plugin_manager` package |

### 6.2 Recommended AGENTX Plugin Types

```python
class AgentXPluginTypes(str, Enum):
    # Memory
    MEMORY = "agentx.plugin.memory"      # Mem0AI backends
    EMBEDDING = "agentx.plugin.embedding"  # ColBERT, OpenAI, etc.

    # AI/ML
    LLM = "agentx.plugin.llm"            # Ollama, OpenAI, etc.
    STT = "agentx.plugin.stt"            # Silero, Whisper
    TTS = "agentx.plugin.tts"            # Silero, Coqui
    VAD = "agentx.plugin.vad"            # Silero VAD, webrtc

    # Data Sources
    SEARCH = "agentx.plugin.search"      # SearXNG, Tavily
    DATABASE = "agentx.plugin.database"  # Qdrant, PostgreSQL
    WEATHER = "agentx.plugin.weather"    # OpenWeatherMap

    # Company MIS
    MIS = "agentx.plugin.mis"            # FastMCP MIS servers

    # Tools
    CALCULATOR = "agentx.plugin.calculator"
    NOTIFIER = "agentx.plugin.notifier"  # Notifications, reminders
```

### 6.3 AGENTX Core Components

```
agentx_core/
├── bus/              # Message/event bus implementation
├── plugin_manager.py # Plugin discovery and lifecycle
├── config.py         # Configuration management
├── agent.py          # DSPy ReAct agent wrapper
└── services/
    ├── memory.py     # Mem0AI integration
    ├── voice.py      # STT/TTS/VAD orchestration
    └── scheduler.py  # Proactive updates
```

### 6.4 AGENTX Plugin Template Example

```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class STTPlugin(ABC):
    """Base class for AGENTX STT plugins."""

    def __init__(self, config: dict):
        self.config = config
        self.sample_rate = config.get("sample_rate", 16000)

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> str:
        """Transcribe audio bytes to text."""
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if plugin dependencies are installed."""
        pass
```

---

## 7. Key Takeaways

### Core Principles

1. **Core orchestrates, plugins implement**
   - Core: lifecycle, communication, configuration
   - Plugins: domain-specific capabilities

2. **Interface segregation via ABCs**
   - Abstract methods define required behavior
   - Plugin authors implement only business logic

3. **Loose coupling via message bus**
   - Components communicate via events
   - Zero direct dependencies

4. **Discovery via entrypoints**
   - No imports needed in core
   - Optional dependencies

5. **Configuration-driven behavior**
   - Plugin selection via config
   - No code changes to swap implementations

### Anti-Patterns to Avoid

- ❌ Core importing plugin implementations directly
- ❌ Plugins depending on other plugins
- ❌ Tightly coupled interfaces (many methods)
- ❌ Hard-coded plugin selection
- ❌ Business logic in core

### Best Practices

- ✅ Abstract base classes for plugin interfaces
- ✅ Message bus for inter-plugin communication
- ✅ Entrypoint-based plugin discovery
- ✅ Configuration-driven plugin loading
- ✅ Plugins work standalone (no core dependency)

---

## 8. References

- **OVOS Core Repository**: https://github.com/OpenVoiceOS/ovos-core
- **OVOS Plugin Manager**: https://github.com/OpenVoiceOS/ovos-plugin-manager
- **OVOS Technical Manual**: https://www.openvoiceos.org/tech-manual/
- **Python Entrypoints**: PEP 421 – Entry Points

---

**Document Status**: Complete
**Next Steps**: Apply these patterns to AGENTX architecture design
