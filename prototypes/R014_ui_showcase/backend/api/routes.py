# =============================================================================
# AGENTX R014 - UI Showcase API Routes
# =============================================================================
# Static UI descriptors with DSPy+Ollama content hydration
# =============================================================================

from typing import Any, Literal

import dspy
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# =============================================================================
# Configure DSPy with Ollama
# =============================================================================

lm = dspy.LM("ollama_chat/gemma3:4b", api_base="http://localhost:11434")
dspy.configure(lm=lm)


# =============================================================================
# DSPy Signatures for Content Generation
# =============================================================================

class MarkdownContentSignature(dspy.Signature):
    """Generate markdown content."""
    topic = dspy.InputField(desc="Topic to write about")
    content = dspy.OutputField(desc="Markdown formatted content")


class CardContentSignature(dspy.Signature):
    """Generate card content."""
    topic = dspy.InputField(desc="Card topic")
    title = dspy.OutputField(desc="Card title")
    content = dspy.OutputField(desc="Card body content")


class WeatherCardSignature(dspy.Signature):
    """Generate weather card content."""
    location = dspy.InputField(desc="City name")
    weather_info = dspy.OutputField(desc="Weather description with emojis")


class SearchResultsSignature(dspy.Signature):
    """Generate search results."""
    query = dspy.InputField(desc="Search query")
    results = dspy.OutputField(desc="List of search results as numbered items")


class FormFieldsSignature(dspy.Signature):
    """Generate form fields description."""
    form_purpose = dspy.InputField(desc="What the form is for")
    fields_description = dspy.OutputField(desc="Form fields needed")


class FormContentSignature(dspy.Signature):
    """Generate full form content."""
    form_type = dspy.InputField(desc="Type of form (login, feedback, survey, etc.)")
    title = dspy.OutputField(desc="Form title")
    description = dspy.OutputField(desc="Form description")


class ProgressContentSignature(dspy.Signature):
    """Generate progress status."""
    task = dspy.InputField(desc="Task being performed")
    status_text = dspy.OutputField(desc="Current status message")


class ActionContentSignature(dspy.Signature):
    """Generate action button text."""
    action_type = dspy.InputField(desc="Type of action (approve, delete, submit, etc.)")
    button_text = dspy.OutputField(desc="Button label")
    description = dspy.OutputField(desc="Action description")


class ConfirmationContentSignature(dspy.Signature):
    """Generate confirmation dialog."""
    action = dspy.InputField(desc="Action to confirm")
    title = dspy.OutputField(desc="Dialog title")
    message = dspy.OutputField(desc="Confirmation message")


# =============================================================================
# Pydantic Models
# =============================================================================

class UIDescriptor(BaseModel):
    """UI descriptor model."""
    id: str
    type: Literal["markdown", "card", "form", "progress", "action", "confirmation", "voice"]
    timestamp: str
    dismissible: bool = True
    content: str | None = None
    title: str | None = None
    metadata: dict[str, Any] = {}


class GenerateRequest(BaseModel):
    """Request to generate content."""
    prompt: str
    widget_type: Literal["markdown", "card", "form", "progress", "action", "confirmation"]


# =============================================================================
# Static UI Descriptor Templates
# =============================================================================

STATIC_TEMPLATES = {
    "markdown": {
        "metadata": {"format": "markdown"}
    },
    "card": {
        "metadata": {"icon": "info", "actions": [{"label": "More Info", "action": "more", "variant": "outline"}]}
    },
    "form": {
        "metadata": {
            "form_id": "dynamic-form",
            "submit_label": "Submit",
            "fields": [
                {"name": "input1", "type": "text", "label": "Your Input", "required": True, "placeholder": "Enter text..."},
                {"name": "input2", "type": "textarea", "label": "Details", "required": False, "placeholder": "Additional details..."}
            ]
        }
    },
    "progress": {
        "metadata": {"value": 0.5, "indeterminate": False, "status_text": "In progress..."}
    },
    "action": {
        "metadata": {"button_text": "Click Me", "action_id": "action_click", "variant": "default"}
    },
    "confirmation": {
        "metadata": {
            "confirm_label": "Confirm",
            "cancel_label": "Cancel",
            "confirm_action": "confirm_yes",
            "cancel_action": "confirm_no",
            "variant": "default"
        }
    },
}


# =============================================================================
# Content Generators
# =============================================================================

class ContentGenerator:
    """Generate dynamic content for UI components using DSPy."""

    @staticmethod
    async def generate_markdown(prompt: str) -> UIDescriptor:
        """Generate markdown content."""
        generator = dspy.Predict(MarkdownContentSignature)
        result = generator(topic=prompt)
        return UIDescriptor(
            id=f"markdown-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            content=result.content,
            metadata={"format": "markdown"}
        )

    @staticmethod
    async def generate_card(prompt: str) -> UIDescriptor:
        """Generate card content."""
        generator = dspy.Predict(CardContentSignature)
        result = generator(topic=prompt)
        return UIDescriptor(
            id=f"card-{datetime.now().timestamp()}",
            type="card",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.content,
            metadata={"icon": "sparkles", "actions": [{"label": "Learn More", "action": "more", "variant": "outline"}]}
        )

    @staticmethod
    async def generate_weather_card(location: str) -> UIDescriptor:
        """Generate weather card content."""
        generator = dspy.Predict(WeatherCardSignature)
        result = generator(location=location)
        return UIDescriptor(
            id=f"card-weather-{datetime.now().timestamp()}",
            type="card",
            timestamp=datetime.now().isoformat(),
            title=f"Weather in {location}",
            content=result.weather_info,
            metadata={"icon": "cloud", "actions": [{"label": "Refresh", "action": "refresh", "variant": "outline"}]}
        )

    @staticmethod
    async def generate_search_results(query: str) -> UIDescriptor:
        """Generate search results card."""
        generator = dspy.Predict(SearchResultsSignature)
        result = generator(query=query)
        return UIDescriptor(
            id=f"card-search-{datetime.now().timestamp()}",
            type="card",
            timestamp=datetime.now().isoformat(),
            title=f"Search Results: {query}",
            content=result.results,
            metadata={"icon": "search", "actions": [{"label": "Refine", "action": "refine", "variant": "default"}]}
        )

    @staticmethod
    async def generate_form(prompt: str) -> UIDescriptor:
        """Generate form content."""
        generator = dspy.Predict(FormContentSignature)
        result = generator(form_type=prompt)
        return UIDescriptor(
            id=f"form-{datetime.now().timestamp()}",
            type="form",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.description,
            metadata={
                "form_id": "dynamic-form",
                "submit_label": "Submit",
                "fields": [
                    {"name": "response", "type": "textarea", "label": "Your Response", "required": True, "placeholder": "Type here..."}
                ]
            }
        )

    @staticmethod
    async def generate_progress(prompt: str) -> UIDescriptor:
        """Generate progress content."""
        generator = dspy.Predict(ProgressContentSignature)
        result = generator(task=prompt)
        return UIDescriptor(
            id=f"progress-{datetime.now().timestamp()}",
            type="progress",
            timestamp=datetime.now().isoformat(),
            title="Processing",
            content=result.status_text,
            metadata={"value": 0.6, "indeterminate": False, "status_text": result.status_text}
        )

    @staticmethod
    async def generate_action(prompt: str) -> UIDescriptor:
        """Generate action button content."""
        generator = dspy.Predict(ActionContentSignature)
        result = generator(action_type=prompt)
        return UIDescriptor(
            id=f"action-{datetime.now().timestamp()}",
            type="action",
            timestamp=datetime.now().isoformat(),
            title=result.description,
            content="Click the button below",
            metadata={"button_text": result.button_text, "action_id": "action_click", "variant": "default"}
        )

    @staticmethod
    async def generate_confirmation(prompt: str) -> UIDescriptor:
        """Generate confirmation dialog content."""
        generator = dspy.Predict(ConfirmationContentSignature)
        result = generator(action=prompt)
        return UIDescriptor(
            id=f"confirmation-{datetime.now().timestamp()}",
            type="confirmation",
            timestamp=datetime.now().isoformat(),
            title=result.title,
            content=result.message,
            metadata={
                "confirm_label": "Confirm",
                "cancel_label": "Cancel",
                "confirm_action": "confirm_yes",
                "cancel_action": "confirm_no",
                "variant": "default"
            }
        )


# =============================================================================
# Routes
# =============================================================================

@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "R014 UI Showcase (DSPy + Ollama)"}


@router.post("/mock/generate")
async def generate_content(request: GenerateRequest) -> UIDescriptor:
    """Generate UI content using DSPy + Ollama."""
    generator = ContentGenerator()

    try:
        if request.widget_type == "markdown":
            return await generator.generate_markdown(request.prompt)
        elif request.widget_type == "card":
            return await generator.generate_card(request.prompt)
        elif request.widget_type == "form":
            return await generator.generate_form(request.prompt)
        elif request.widget_type == "progress":
            return await generator.generate_progress(request.prompt)
        elif request.widget_type == "action":
            return await generator.generate_action(request.prompt)
        elif request.widget_type == "confirmation":
            return await generator.generate_confirmation(request.prompt)
        else:
            raise ValueError(f"Unknown widget type: {request.widget_type}")
    except Exception as e:
        # Fallback on error
        return UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type=request.widget_type,
            timestamp=datetime.now().isoformat(),
            title="Generation Error",
            content=f"Could not generate content: {str(e)}",
            metadata={"error": True}
        )


@router.get("/mock/descriptors")
async def get_example_descriptors() -> list[UIDescriptor]:
    """Get static example UI descriptors."""
    return [
        UIDescriptor(
            id="markdown-1",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            content="# Welcome to AGENTX UI Showcase\n\nThis showcase uses **DSPy + Ollama** to generate dynamic content for static UI components.\n\nClick **Generate** to see it in action!",
            metadata={"format": "markdown"}
        ),
        UIDescriptor(
            id="card-1",
            type="card",
            timestamp=datetime.now().isoformat(),
            title="About This Showcase",
            content="UI descriptors are **static** (7 fixed types), but content is **dynamic** via DSPy + gemma3:4b.",
            metadata={"icon": "info", "actions": [{"label": "Learn More", "action": "more", "variant": "outline"}]}
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
                    {"name": "widget_type", "type": "select", "label": "Widget Type", "required": True, "options": ["markdown", "card", "form", "progress", "action", "confirmation"]},
                    {"name": "prompt", "type": "textarea", "label": "Prompt", "required": True, "placeholder": "e.g., A poem about artificial intelligence"}
                ]
            }
        ),
        UIDescriptor(
            id="progress-1",
            type="progress",
            timestamp=datetime.now().isoformat(),
            title="DSPy Status",
            content="LLM is ready to generate content",
            metadata={"value": 1.0, "indeterminate": False, "status_text": "Ready"}
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
            "widget_count": 6
        },
        {
            "id": "session-2",
            "title": "UI Exploration",
            "date": datetime.now().isoformat(),
            "summary": "Explored all 7 generative UI widget types.",
            "widget_count": 7
        }
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
            "description": "Local LLM (gemma3:4b) - Generates widget content"
        },
        {
            "id": "dspy",
            "name": "DSPy Framework",
            "type": "framework",
            "status": "connected",
            "url": "https://github.com/stanfordnlp/dspy",
            "description": "Programmatic LLM interface - Content generation"
        }
    ]
