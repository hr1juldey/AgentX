"""Tests for LangGraph state transitions.

Verifies that all 8 nodes properly update AgentState.
Uses real Ollama with small LLM (deepseek-r1:1.5b) for integration tests.
These tests are marked as integration since they make real LLM calls.
"""
