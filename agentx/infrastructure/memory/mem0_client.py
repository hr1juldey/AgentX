"""Mem0AI client wrapper for AGENTX.

This module provides backward-compatible re-exports from the mem0/ subdirectory.
The actual implementation has been split into focused modules:
- client.py: Main Mem0Client class
- config.py: Mem0AI configuration builder
- result_parser.py: Search result parsing utilities
"""

from agentx.infrastructure.memory.mem0.client import Mem0Client

__all__ = ["Mem0Client"]
