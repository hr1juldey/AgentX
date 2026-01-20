# =============================================================================
# AGENTX R014 - Example Data Endpoints
# =============================================================================
# Static mock data for UI showcase
# =============================================================================

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from api.models import UIDescriptor

router = APIRouter()


# =============================================================================
# Example Descriptors
# =============================================================================


@router.get("/mock/descriptors")
async def get_example_descriptors() -> list[UIDescriptor]:
    """Get static example UI descriptors."""
    return [
        UIDescriptor(
            id="markdown-1",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            content="# Welcome to AGENTX UI Showcase\n\nThis showcase uses **DSPy + Ollama** to generate dynamic content for static UI components.\n\nClick **Generate** to see it in action!",
            metadata={"format": "markdown"},
        ),
        UIDescriptor(
            id="card-1",
            type="card",
            timestamp=datetime.now().isoformat(),
            title="About This Showcase",
            content="UI descriptors are **static** (7 fixed types), but content is **dynamic** via DSPy + gemma3:4b.",
            metadata={
                "icon": "info",
                "actions": [
                    {"label": "Learn More", "action": "more", "variant": "outline"}
                ],
            },
        ),
        UIDescriptor(
            id="form-1",
            type="form",
            timestamp=datetime.now().isoformat(),
            title="Try Content Generation",
            content="Enter a prompt to generate dynamic content for any widget type:",
            metadata={
                "form_id": "generate",
                "submit_label": "Generate",
                "fields": [
                    {
                        "name": "widget_type",
                        "type": "select",
                        "label": "Widget Type",
                        "required": True,
                        "options": [
                            "markdown",
                            "card",
                            "form",
                            "progress",
                            "action",
                            "confirmation",
                        ],
                    },
                    {
                        "name": "prompt",
                        "type": "textarea",
                        "label": "Prompt",
                        "required": True,
                        "placeholder": "e.g., A poem about artificial intelligence",
                    },
                ],
            },
        ),
        UIDescriptor(
            id="progress-1",
            type="progress",
            timestamp=datetime.now().isoformat(),
            title="DSPy Status",
            content="LLM is ready to generate content",
            metadata={"value": 1.0, "indeterminate": False, "status_text": "Ready"},
        ),
    ]


@router.get("/mock/descriptors/types/list")
async def list_descriptor_types() -> list[str]:
    """List all available descriptor types."""
    return ["markdown", "card", "form", "progress", "action", "confirmation", "voice"]


@router.get("/mock/sessions")
async def get_past_sessions() -> list[dict[str, Any]]:
    """Get example past sessions."""
    return [
        {
            "id": "session-1",
            "title": "Content Generation Tests",
            "date": datetime.now().isoformat(),
            "summary": "Generated various content types using DSPy + Ollama.",
            "widget_count": 6,
        },
        {
            "id": "session-2",
            "title": "UI Exploration",
            "date": datetime.now().isoformat(),
            "summary": "Explored all 7 generative UI widget types.",
            "widget_count": 7,
        },
    ]


@router.get("/mock/connectors")
async def get_data_connectors() -> list[dict[str, Any]]:
    """Get data connectors status."""
    return [
        {
            "id": "ollama",
            "name": "Ollama LLM",
            "type": "llm",
            "status": "connected",
            "url": "http://localhost:11434",
            "description": "Local LLM (gemma3:4b) - Generates widget content",
        },
        {
            "id": "dspy",
            "name": "DSPy Framework",
            "type": "framework",
            "status": "connected",
            "url": "https://github.com/stanfordnlp/dspy",
            "description": "Programmatic LLM interface - Content generation",
        },
    ]
