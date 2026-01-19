# AGENTX Plugin System LLD

**Version**: 1.0.0
**Date**: 2026-01-19
**Status**: Locked
**Dependencies**: domain_model.md

---

## Table of Contents

1. [Plugin Interface](#1-plugin-interface)
2. [Plugin Permissions](#2-plugin-permissions)
3. [Plugin Manifest](#3-plugin-manifest)
4. [Plugin Registry](#4-plugin-registry)
5. [Plugin Lifecycle](#5-plugin-lifecycle)
6. [Plugin Security](#6-plugin-security)

---

## 1. Plugin Interface

### 1.1 AgentXPlugin Abstract Base Class

**File**: `plugin/interface.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID

import dspy

from plugin.permissions import PluginPermissions
from plugin.manifest import PluginManifest
from ui.descriptors.base import UIDescriptorType


class AgentXPlugin(ABC):
    """Abstract base class for all AGENTX plugins.

    Plugins must implement all abstract methods.
    """

    # Plugin metadata (set by subclass)
    plugin_id: str
    plugin_name: str
    plugin_version: str
    permissions: PluginPermissions

    @abstractmethod
    async def register_tools(self) -> List[dspy.Tool]:
        """Register tools provided by this plugin.

        Returns:
            List of dspy.Tool instances for agent use.

        Example:
            def my_tool(param: str) -> str:
                return f"Processed: {param}"

            return [dspy.Tool(my_tool)]
        """
        pass

    @abstractmethod
    async def on_install(self) -> "InstallationResult":
        """Called when plugin is installed.

        Returns:
            InstallationResult with success status and message.

        Use for:
            - Data migration
            - Configuration setup
            - Dependency checks
        """
        pass

    @abstractmethod
    async def on_uninstall(self) -> "UninstallationResult":
        """Called when plugin is uninstalled.

        Returns:
            UninstallationResult with success status and message.

        Use for:
            - Data cleanup
            - Resource deallocation
            - Configuration removal
        """
        pass

    @abstractmethod
    async def on_enable(self) -> None:
        """Called when plugin is enabled.

        Use for:
            - Starting background tasks
            - Registering event handlers
            - Initializing resources
        """
        pass

    @abstractmethod
    async def on_disable(self) -> None:
        """Called when plugin is disabled.

        Use for:
            - Stopping background tasks
            - Unregistering event handlers
            - Releasing resources
        """
        pass

    @abstractmethod
    async def health_check(self) -> "HealthStatus":
        """Check if plugin is healthy.

        Returns:
            HealthStatus with is_healthy flag and message.

        Called periodically to monitor plugin status.
        """
        pass

    # Optional UI descriptor methods

    async def can_create_ui_descriptor(self, descriptor_type: UIDescriptorType) -> bool:
        """Check if plugin can create specific UI descriptor type.

        Default: False (plugins need opt-in permission)

        Args:
            descriptor_type: Type of UI descriptor

        Returns:
            True if plugin has permission and capability
        """
        if not self.permissions.allow_ui_descriptors:
            return False
        return descriptor_type in self.permissions.allowed_ui_types

    async def create_ui_descriptor(
        self,
        descriptor_type: UIDescriptorType,
        config: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Create a UI descriptor (if permitted).

        Args:
            descriptor_type: Type of UI descriptor to create
            config: Configuration for the descriptor

        Returns:
            Descriptor data or None if not permitted/able
        """
        if not await self.can_create_ui_descriptor(descriptor_type):
            return None

        # Override in subclass to implement
        return None

    # Optional memory access methods

    async def can_access_memory(self) -> bool:
        """Check if plugin can access user memory."""
        return self.permissions.allow_memory_access

    async def search_user_memories(
        self,
        query: str,
        user_id: str,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """Search user memories (if permitted).

        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum results

        Returns:
            Memory results or None if not permitted
        """
        if not await self.can_access_memory():
            return None

        # Override in subclass or use injected repository
        return None
```

### 1.2 Plugin Data Classes

**File**: `plugin/types.py`

```python
from dataclasses import dataclass
from typing import Optional


@dataclass
class InstallationResult:
    """Result of plugin installation."""

    success: bool
    message: str
    data_files_created: list[str] = None

    def __post_init__(self):
        if self.data_files_created is None:
            self.data_files_created = []


@dataclass
class UninstallationResult:
    """Result of plugin uninstallation."""

    success: bool
    message: str
    data_files_removed: list[str] = None

    def __post_init__(self):
        if self.data_files_removed is None:


@dataclass
class HealthStatus:
    """Plugin health status."""

    is_healthy: bool
    message: str
    details: dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
```

---

## 2. Plugin Permissions

### 2.1 PluginPermissions Model

**File**: `plugin/permissions.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from ui.descriptors.base import UIDescriptorType


class PluginPermissions(BaseModel):
    """Permissions granted to a plugin.

    Default: Safe by default (all permissions false).
    Philosophy: User must explicitly grant permissions.
    """

    # UI descriptor permissions
    allow_ui_descriptors: bool = Field(
        default=False,
        description="Allow plugin to create UI descriptors"
    )
    allowed_ui_types: List[UIDescriptorType] = Field(
        default_factory=list,
        description="Specific UI types plugin can create (empty = none)"
    )

    # Memory access permissions
    allow_memory_access: bool = Field(
        default=False,
        description="Allow plugin to access user memory"
    )
    max_memory_results: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum memory results per query"
    )

    # Network permissions
    allow_network_access: bool = Field(
        default=False,
        description="Allow plugin to make network requests"
    )
    allowed_network_hosts: List[str] = Field(
        default_factory=list,
        description="Allowed hostnames (empty = deny all)"
    )

    # Resource quotas
    max_cpu_percent: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Maximum CPU usage percentage"
    )
    max_memory_mb: int = Field(
        default=512,
        ge=64,
        le=4096,
        description="Maximum memory usage in MB"
    )
    max_execution_time_seconds: int = Field(
        default=30,
        ge=5,
        le=300,
        description="Maximum execution time per operation"
    )

    # File system permissions
    allow_file_read: bool = Field(
        default=False,
        description="Allow plugin to read files"
    )
    allow_file_write: bool = Field(
        default=False,
        description="Allow plugin to write files"
    )
    allowed_file_paths: List[str] = Field(
        default_factory=list,
        description="Allowed file paths (empty = deny all)"
    )

    # Tool permissions
    allow_tool_registration: bool = Field(
        default=True,
        description="Allow plugin to register tools (default: true)"
    )
    max_tools: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of tools plugin can register"
    )

    @field_validator("allowed_ui_types")
    def validate_ui_types(cls, v, info):
        """Ensure UI types are valid if allow_ui_descriptors is true."""
        if info.data.get("allow_ui_descriptors", False) and not v:
            # If UI descriptors allowed, must specify types
            raise ValueError("allowed_ui_types must be specified if allow_ui_descriptors is true")
        return v

    @field_validator("allowed_network_hosts")
    def validate_network_hosts(cls, v, info):
        """Ensure network hosts are specified if network access allowed."""
        if info.data.get("allow_network_access", False) and not v:
            raise ValueError("allowed_network_hosts must be specified if allow_network_access is true")
        return v

    def has_ui_permission(self, descriptor_type: UIDescriptorType) -> bool:
        """Check if plugin has permission for specific UI type."""
        return self.allow_ui_descriptors and descriptor_type in self.allowed_ui_types

    def has_network_permission(self, host: str) -> bool:
        """Check if plugin has permission for specific host."""
        if not self.allow_network_access:
            return False
        if not self.allowed_network_hosts:
            return False
        return host in self.allowed_network_hosts

    def has_file_permission(self, file_path: str) -> bool:
        """Check if plugin has permission for specific file path."""
        if not (self.allow_file_read or self.allow_file_write):
            return False
        if not self.allowed_file_paths:
            return False
        return any(
            file_path.startswith(allowed_path)
            for allowed_path in self.allowed_file_paths
        )


# Default permission presets

class PluginPermissionPresets:
    """Pre-defined permission presets for common plugin types."""

    @staticmethod
    def minimal() -> PluginPermissions:
        """Minimal permissions (tools only, no data access)."""
        return PluginPermissions(
            allow_ui_descriptors=False,
            allow_memory_access=False,
            allow_network_access=False,
            allow_file_read=False,
            allow_file_write=False,
        )

    @staticmethod
    def data_source() -> PluginPermissions:
        """Data source plugin (read-only file access, no UI)."""
        return PluginPermissions(
            allow_ui_descriptors=False,
            allow_memory_access=False,
            allow_network_access=False,
            allow_file_read=True,
            allow_file_write=False,
            allowed_file_paths=["/data/shared/"],
        )

    @staticmethod
    def ui_extension() -> PluginPermissions:
        """UI extension plugin (can create UI descriptors)."""
        return PluginPermissions(
            allow_ui_descriptors=True,
            allowed_ui_types=[
                UIDescriptorType.CARD,
                UIDescriptorType.MARKDOWN_BLOCK,
            ],
            allow_memory_access=False,
            allow_network_access=False,
            allow_file_read=False,
            allow_file_write=False,
        )

    @staticmethod
    def full_access() -> PluginPermissions:
        """Full access (use with extreme caution)."""
        return PluginPermissions(
            allow_ui_descriptors=True,
            allowed_ui_types=list(UIDescriptorType),
            allow_memory_access=True,
            allow_network_access=True,
            allowed_network_hosts=["*"],  # All hosts
            allow_file_read=True,
            allow_file_write=True,
            allowed_file_paths=["*"],  # All paths
        )
```

---

## 3. Plugin Manifest

### 3.1 PluginManifest Model

**File**: `plugin/manifest.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from semver import VersionInfo

from plugin.permissions import PluginPermissions


class PluginManifest(BaseModel):
    """Plugin manifest with metadata and permissions.

    Must be signed and included with plugin package.
    """

    # Identity
    plugin_id: str = Field(..., description="Unique plugin identifier (reverse domain notation)")
    plugin_name: str = Field(..., description="Human-readable plugin name")
    plugin_version: str = Field(..., description="Version (semver)")
    description: str = Field(..., description="Plugin description")
    author: str = Field(..., description="Plugin author")
    author_email: Optional[str] = Field(None, description="Author email")

    # Compatibility
    min_agentx_version: str = Field(..., description="Minimum AGENTX version required")
    max_agentx_version: Optional[str] = Field(None, description="Maximum AGENTX version (if incompatible)")

    # Dependencies
    dependencies: List[str] = Field(default_factory=list, description="Required dependencies")
    python_version: str = Field(default=">=3.9", description="Required Python version")

    # Permissions
    permissions: PluginPermissions = Field(..., description="Plugin permissions")

    # Security
    signature: str = Field(..., description="GPG signature of manifest")
    checksum: str = Field(..., description="SHA-256 checksum of plugin code")

    # Metadata
    homepage_url: Optional[str] = Field(None, description="Plugin homepage")
    repository_url: Optional[str] = Field(None, description="Source code repository")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    license: str = Field(default="MIT", description="Plugin license")
    tags: List[str] = Field(default_factory=list, description="Plugin tags for discovery")

    @field_validator("plugin_id")
    def validate_plugin_id(cls, v):
        """Validate plugin ID format (reverse domain notation)."""
        parts = v.split(".")
        if len(parts) < 2:
            raise ValueError("plugin_id must use reverse domain notation (e.g., com.example.plugin)")
        for part in parts:
            if not part.isalnum() and "_" not in part and "-" not in part:
                raise ValueError(f"Invalid plugin_id part: {part}")
        return v

    @field_validator("plugin_version")
    def validate_version(cls, v):
        """Validate version is valid semver."""
        try:
            VersionInfo.parse(v)
        except ValueError as e:
            raise ValueError(f"Invalid semver version: {e}") from e
        return v

    @field_validator("min_agentx_version", "max_agentx_version")
    def validate_agentx_version(cls, v):
        """Validate AGENTX version is valid semver."""
        if v is None:
            return v
        try:
            VersionInfo.parse(v)
        except ValueError as e:
            raise ValueError(f"Invalid semver version: {e}") from e
        return v

    @field_validator("checksum")
    def validate_checksum(cls, v):
        """Validate SHA-256 checksum format."""
        if len(v) != 64:
            raise ValueError("Checksum must be 64 characters (SHA-256)")
        if not all(c in "0123456789abcdef" for c in v):
            raise ValueError("Checksum must be hexadecimal")
        return v
```

### 3.2 Manifest Example

**File**: `plugin/example_manifest.py`

```python
from plugin.manifest import PluginManifest
from plugin.permissions import PluginPermissions, PluginPermissionPresets


# Example: SearXNG search plugin manifest
searxng_manifest = PluginManifest(
    plugin_id="agentx.plugin.searxng",
    plugin_name="SearXNG Search",
    plugin_version="1.0.0",
    description="Web search using SearXNG",
    author="AGENTX Team",
    min_agentx_version="1.0.0",
    dependencies=["aiohttp"],
    permissions=PluginPermissionPresets.minimal(),
    signature="-----BEGIN PGP SIGNATURE-----\n...",
    checksum="a1b2c3d4e5f6..." * 8,
    homepage_url="https://agentx.ai/plugins/searxng",
    repository_url="https://github.com/agentx/searxng-plugin",
    license="MIT",
    tags=["search", "web", "information"],
)
```

---

## 4. Plugin Registry

### 4.1 PluginRegistry Class

**File**: `plugin/registry.py`

```python
from typing import Dict, List, Optional
from pathlib import Path
import asyncio

from plugin.interface import AgentXPlugin
from plugin.manifest import PluginManifest
from plugin.types import HealthStatus


class PluginRegistry:
    """Central registry for plugin management.

    Responsibilities:
        - Plugin discovery and loading
        - Lifecycle management (install, enable, disable, uninstall)
        - Permission enforcement
        - Health monitoring
    """

    def __init__(self, plugins_dir: str = "plugins"):
        self._plugins_dir = Path(plugins_dir)
        self._plugins_dir.mkdir(parents=True, exist_ok=True)

        self._plugins: Dict[str, AgentXPlugin] = {}
        self._manifests: Dict[str, PluginManifest] = {}

        self._enabled_plugins: set[str] = set()
        self._health_status: Dict[str, HealthStatus] = {}

    async def discover_plugins(self) -> List[PluginManifest]:
        """Discover available plugins from filesystem.

        Returns:
            List of discovered plugin manifests
        """
        manifests = []

        for plugin_path in self._plugins_dir.iterdir():
            if not plugin_path.is_dir():
                continue

            manifest_file = plugin_path / "manifest.json"
            if not manifest_file.exists():
                continue

            try:
                manifest = PluginManifest.model_validate_json(
                    manifest_file.read_text()
                )
                manifests.append(manifest)
            except Exception:
                continue

        return manifests

    async def install_plugin(self, plugin_path: str) -> bool:
        """Install a plugin from path.

        Args:
            plugin_path: Path to plugin package

        Returns:
            True if installation successful
        """
        # Validate plugin
        plugin = await self._load_plugin(plugin_path)
        result = await plugin.on_install()

        if result.success:
            self._plugins[plugin.plugin_id] = plugin
            self._manifests[plugin.plugin_id] = plugin.manifest

        return result.success

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin to uninstall

        Returns:
            True if uninstallation successful
        """
        if plugin_id not in self._plugins:
            return False

        # Disable first
        await self.disable_plugin(plugin_id)

        # Call uninstall hook
        plugin = self._plugins[plugin_id]
        result = await plugin.on_uninstall()

        if result.success:
            del self._plugins[plugin_id]
            del self._manifests[plugin_id]

        return result.success

    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin.

        Args:
            plugin_id: Plugin to enable

        Returns:
            True if enabled successfully
        """
        if plugin_id not in self._plugins:
            return False

        plugin = self._plugins[plugin_id]
        await plugin.on_enable()
        self._enabled_plugins.add(plugin_id)

        return True

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin.

        Args:
            plugin_id: Plugin to disable

        Returns:
            True if disabled successfully
        """
        if plugin_id not in self._enabled_plugins:
            return False

        plugin = self._plugins[plugin_id]
        await plugin.on_disable()
        self._enabled_plugins.remove(plugin_id)

        return True

    async def get_plugin_tools(self, plugin_id: str) -> List:
        """Get tools provided by a plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            List of dspy.Tool instances
        """
        if plugin_id not in self._plugins or plugin_id not in self._enabled_plugins:
            return []

        plugin = self._plugins[plugin_id]
        return await plugin.register_tools()

    async def check_health(self, plugin_id: str) -> Optional[HealthStatus]:
        """Check plugin health.

        Args:
            plugin_id: Plugin to check

        Returns:
            Health status or None if plugin not found
        """
        if plugin_id not in self._plugins:
            return None

        plugin = self._plugins[plugin_id]
        status = await plugin.health_check()
        self._health_status[plugin_id] = status
        return status

    async def check_all_health(self) -> Dict[str, HealthStatus]:
        """Check health of all enabled plugins.

        Returns:
            Dict mapping plugin_id to health status
        """
        results = {}

        for plugin_id in self._enabled_plugins:
            results[plugin_id] = await self.check_health(plugin_id)

        return results

    def is_enabled(self, plugin_id: str) -> bool:
        """Check if plugin is enabled."""
        return plugin_id in self._enabled_plugins

    def get_plugin(self, plugin_id: str) -> Optional[AgentXPlugin]:
        """Get plugin instance by ID."""
        return self._plugins.get(plugin_id)

    def get_manifest(self, plugin_id: str) -> Optional[PluginManifest]:
        """Get plugin manifest by ID."""
        return self._manifests.get(plugin_id)

    def list_plugins(self) -> List[str]:
        """List all installed plugin IDs."""
        return list(self._plugins.keys())

    def list_enabled_plugins(self) -> List[str]:
        """List enabled plugin IDs."""
        return list(self._enabled_plugins)

    async def _load_plugin(self, plugin_path: str) -> AgentXPlugin:
        """Load plugin from path (private)."""
        # Import plugin module
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get plugin class
        plugin_class = getattr(module, "Plugin")
        return plugin_class()
```

---

## 5. Plugin Lifecycle

### 5.1 State Machine

```
INSTALLED → ENABLED → DISABLED → UNINSTALLED
              ↑        ↓
              └────────┘
```

### 5.2 Lifecycle Hooks

| Event | Hook Called | Purpose |
|-------|-------------|---------|
| Install | `on_install()` | Setup, config, migration |
| Enable | `on_enable()` | Start tasks, register handlers |
| Disable | `on_disable()` | Stop tasks, cleanup |
| Uninstall | `on_uninstall()` | Remove data, cleanup |
| Periodic | `health_check()` | Health monitoring |

### 5.3 Background Install

**Policy**: Plugins install in background, require restart to use.

```python
async def install_plugin_background(plugin_path: str) -> str:
    """Install plugin in background (non-blocking)."""
    plugin_id = extract_plugin_id(plugin_path)

    # Run installation in background task
    asyncio.create_task(_install_plugin_task(plugin_path))

    return plugin_id


async def _install_plugin_task(plugin_path: str):
    """Background task for plugin installation."""
    try:
        await registry.install_plugin(plugin_path)
        # Notify user when ready
        await notify_plugin_ready(plugin_id)
    except Exception as e:
        await notify_plugin_error(plugin_id, str(e))
```

---

## 6. Plugin Security

### 6.1 Code Signing

**Policy**: All plugins must be GPG-signed.

```python
import gnupg

def verify_plugin_signature(manifest: PluginManifest, plugin_dir: Path) -> bool:
    """Verify GPG signature of plugin."""
    gpg = gnupg.GPG()

    # Verify manifest signature
    verified = gpg.verify(manifest.signature)

    if not verified.valid:
        return False

    # Verify checksum
    import hashlib
    with open(plugin_dir / "plugin.py", "rb") as f:
        code_hash = hashlib.sha256(f.read()).hexdigest()

    return code_hash == manifest.checksum
```

### 6.2 Sandboxing

**Policy**: Resource quotas and process isolation.

```python
import resource

def enforce_plugin_quotas(permissions: PluginPermissions):
    """Enforce resource quotas for plugin."""
    # CPU limit (via cgroups on Linux)
    # Memory limit
    resource.setrlimit(
        resource.RLIMIT_AS,
        (permissions.max_memory_mb * 1024 * 1024, permissions.max_memory_mb * 1024 * 1024)
    )

    # Execution time limit (via timeout decorator)
    # Network access control (via firewall rules)
```

### 6.3 Permission Checks

**Before executing plugin operation:**

```python
async def safe_plugin_operation(
    plugin: AgentXPlugin,
    operation: str,
    **kwargs
) -> Any:
    """Execute plugin operation with permission checks."""
    permissions = plugin.permissions

    # Check permission for operation
    if operation == "ui_descriptor":
        if not permissions.allow_ui_descriptors:
            raise PermissionError("Plugin does not have UI descriptor permission")

    elif operation == "memory_access":
        if not permissions.allow_memory_access:
            raise PermissionError("Plugin does not have memory access permission")

    elif operation == "network":
        if not permissions.allow_network_access:
            raise PermissionError("Plugin does not have network permission")
        host = kwargs.get("host")
        if not permissions.has_network_permission(host):
            raise PermissionError(f"Plugin does not have permission for host: {host}")

    # Execute with timeout
    import asyncio
    try:
        result = await asyncio.wait_for(
            operation(**kwargs),
            timeout=permissions.max_execution_time_seconds
        )
        return result
    except asyncio.TimeoutError:
        raise TimeoutError("Plugin operation exceeded time limit")
```

---

**This plugin system document is part of AGENTX LLD v1.0. All names and types are locked.**
