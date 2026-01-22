# =============================================================================
# AGENTX R014 - UI Showcase API Routes
# =============================================================================
# API endpoints for UI showcase
# =============================================================================

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from api.content_generator import ContentGenerator
from api.models import GenerateRequest, UIDescriptor, IntelligentGenerateRequest
from api.routes_examples import router as examples_router
from config.dspy import configure_dspy, get_lm_info
from config.settings import settings
from services.widget_spawner import get_widget_spawner_service
from services.widget_spawner.intelligent_agent import IntelligentUIGenerator
from services.multihop_search.agents import MultiHopSearchAgent
from services.multihop_search.schemas import HopEvent, SearchRequest

# Master Agent imports
from services.master_agent import create_master_agent, DeliveryPlan
from services.pipeline.analyst import AnalystAgent
from services.pipeline.researcher import ResearcherAgent
from services.pipeline.data_contextualizer import DataContextualizerAgent
from services.pipeline.designer import DesignerAgent
from services.pipeline.widget_selector import WidgetSelectorAgent
from services.pipeline.sequencer import SequencerAgent
from services.pipeline.presenter import PresenterAgent
from services.hydrators.card_hydrator import CardHydrator
from services.hydrators.chart_hydrator import ChartHydrator
from services.hydrators.form_hydrator import FormHydrator
from services.hydrators.gallery_hydrator import GalleryHydrator
from services.hydrators.image_hydrator import ImageHydrator
from services.hydrators.markdown_hydrator import MarkdownHydrator

router = APIRouter()
logger = logging.getLogger(__name__)

# Include example data endpoints
router.include_router(examples_router)

# =============================================================================
# Configure DSPy with LLM from environment settings
# =============================================================================

# Configure DSPy once at module load using settings from .env
configure_dspy()


# =============================================================================
# Health Check
# =============================================================================


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Health check endpoint with LLM configuration info."""
    lm_info = get_lm_info()
    return {
        "status": "healthy",
        "service": "R014 UI Showcase (DSPy Generative UI)",
        "llm": lm_info,
    }


# =============================================================================
# Widget Generation Endpoints
# =============================================================================


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
        elif request.widget_type == "image":
            return await generator.generate_image(request.prompt)
        elif request.widget_type == "gallery":
            return await generator.generate_gallery(request.prompt)
        elif request.widget_type == "chart":
            return await generator.generate_chart(request.prompt)
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
            metadata={"error": True},
        )


@router.post("/generate-widget")
async def generate_widget(request: GenerateRequest) -> dict[str, Any]:
    """Generate widget(s) using DSPy ReAct agent with automatic widget selection.

    This endpoint uses a DSPy ReAct agent that:
    1. Automatically analyzes what widgets are needed based on the query
    2. Can generate multiple widgets (e.g., chart + summary markdown)
    3. Returns a list of complete UI descriptors ready for rendering

    Unlike /mock/generate, this endpoint does NOT require widget_type to be specified.
    If widget_type is provided, it will force that type and skip ReAct reasoning.

    Returns:
        {
            "widgets": [...],  // List of UIDescriptor objects
            "tools_used": [...],  // Optional: list of tools called by ReAct
            "reasoning": "..."  // Optional: ReAct reasoning trace
        }
    """
    logger.debug(
        f"🔵 /generate-widget called: prompt='{request.prompt}', widget_type={request.widget_type}"
    )

    service = get_widget_spawner_service()

    try:
        # widget_type is optional - if None, multi-widget ReAct agent will decide
        logger.debug("🔵 Calling service.generate_widget...")
        response = await service.generate_widget(
            prompt=request.prompt,
            widget_type=request.widget_type if request.widget_type else None,
        )

        logger.debug(f"🔵 Service returned {len(response.widgets)} widgets")
        for i, widget in enumerate(response.widgets):
            logger.debug(
                f"🔵   Widget {i + 1}: id={widget.id}, type={widget.type}, title={widget.title}"
            )

        # Convert all WidgetDescriptors to UIDescriptor format for frontend compatibility
        widgets = [
            UIDescriptor(
                id=widget.id,
                type=widget.type,
                timestamp=datetime.now().isoformat(),
                title=widget.title,
                content=widget.content,
                metadata=widget.metadata or {},
                dismissible=widget.dismissible,
            )
            for widget in response.widgets
        ]

        result = {
            "widgets": widgets,
            "tools_used": response.tools_used,
            "reasoning": response.reasoning,
        }
        logger.debug(f"🔵 Returning result: {len(result['widgets'])} widgets")
        return result
    except Exception as e:
        # Fallback on error - return single markdown widget with error message
        logger.error(f"🔴 Error generating widget: {e}", exc_info=True)
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Widget Generation Error",
            content=f"**Error:** {str(e)}\n\nThe DSPy agent encountered an error while generating widgets.",
            metadata={"error": True, "format": "markdown"},
        )
        return {"widgets": [error_widget], "tools_used": None, "reasoning": None}


@router.post("/generate-intelligent")
async def generate_intelligent(request: IntelligentGenerateRequest) -> dict[str, Any]:
    """Generate intelligent UI using three-tier DSPy architecture.

    This endpoint uses advanced DSPy patterns for automatic decision-making:
    1. ReAct - Context analysis (content type, user intent, device awareness)
    2. BestOfN - Generate 5 presentation options, select best
    3. Refine - Self-improve accessibility until WCAG AA compliance

    Key differences from /generate-widget:
    - NO widget_type required - system decides automatically
    - Device-aware layout selection (mobile vs desktop)
    - Automatic color scheme generation
    - Optional position suggestions (x, y coordinates)
    - WCAG accessibility validation

    Returns:
        {
            "widgets": [...],  // List of UIDescriptor with optional x, y
            "layout": "...",  // Selected layout pattern
            "design_system": {...},  // Color scheme, typography
            "reasoning": "..."  // Agent's reasoning
        }
    """
    logger.info(
        f"🤖 /generate-intelligent called: prompt='{request.prompt}', "
        f"device={request.device_context.get('type')}"
    )

    try:
        # Create intelligent generator
        generator = IntelligentUIGenerator()

        # Generate intelligent UI
        result = generator(
            user_query=request.prompt, device_context=request.device_context
        )

        # Convert widgets to UIDescriptor format
        widgets = [
            UIDescriptor(
                id=w.get("id", ""),
                type=w.get("type", "markdown"),
                timestamp=datetime.now().isoformat(),
                title=w.get("title"),
                content=w.get("content"),
                dismissible=w.get("dismissible", True),
                metadata=w.get("metadata", {}),
            )
            for w in result.widgets
        ]

        response = {
            "widgets": widgets,
            "layout": result.layout,
            "design_system": result.design_system,
            "reasoning": result.reasoning,
        }

        logger.info(f"🤖 Generated {len(widgets)} widgets with layout: {result.layout}")
        return response

    except Exception as e:
        logger.error(f"🤖 Error in intelligent generation: {e}", exc_info=True)
        # Fallback - return single markdown widget with error
        error_widget = UIDescriptor(
            id=f"error-{datetime.now().timestamp()}",
            type="markdown",
            timestamp=datetime.now().isoformat(),
            title="Intelligent Generation Error",
            content=f"**Error:** {str(e)}\n\nThe intelligent agent encountered an error.",
            metadata={"error": True, "format": "markdown"},
        )
        return {
            "widgets": [error_widget],
            "layout": "simple_vertical",
            "design_system": {},
            "reasoning": f"Error: {str(e)}",
        }


# =============================================================================
# Multi-Hop Search Endpoints
# =============================================================================


@router.post("/search")
async def search_endpoint(request: dict[str, Any]) -> dict[str, Any]:
    """REST endpoint for multi-hop search (non-streaming).

    Args:
        request: Search request with 'query' field

    Returns:
        Search result with answer, citations, and metadata
    """
    query = request.get("query", "")
    max_hops = request.get("max_hops", settings.max_hops)

    logger.info(f"🔍 /search called: query='{query[:50]}...'")

    try:
        agent = MultiHopSearchAgent(
            max_hops=max_hops,
            stop_threshold=settings.stop_threshold,
        )

        result = await agent(question=query)

        # Convert to search result
        return {
            "answer": result.answer,
            "summary": getattr(result, "summary", ""),
            "confidence": getattr(result, "confidence", "medium"),
            "citations": result.citations or [],
            "hops": result.hops or [],
            "metadata": result.metadata or {},
            "queries_used": result.metadata.get("queries_used", [])
            if result.metadata
            else [],
        }
    except Exception as e:
        logger.error(f"🔴 Error in search: {e}", exc_info=True)
        return {
            "answer": f"Error: {str(e)}",
            "summary": "",
            "confidence": "low",
            "citations": [],
            "hops": [],
            "metadata": {"error": True},
            "queries_used": [],
        }


@router.websocket("/ws/search")
async def search_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for streaming multi-hop search progress.

    Sends events in real-time:
    - hop_event: Progress updates for each hop
    - final_result: Final synthesized answer

    Client should send:
    {"query": "your question", "max_hops": 5}
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    logger.info(f"🔍 WebSocket search connected: {session_id}")

    try:
        # Receive initial request
        data = await websocket.receive_json()
        request = SearchRequest(**data)

        logger.info(
            f"🔍 Search request: query='{request.query[:50]}...', "
            f"max_hops={request.max_hops}"
        )

        # Progress callback for WebSocket
        async def send_progress(event: HopEvent) -> None:
            await websocket.send_json(
                {
                    "type": "hop_event",
                    "data": event.model_dump(),
                }
            )

        # Create agent with progress callback
        agent = MultiHopSearchAgent(
            max_hops=request.max_hops or settings.max_hops,
            progress_callback=send_progress,
            stop_threshold=settings.stop_threshold,
        )

        # Run search
        result = await agent(question=request.query)

        # Build citations for response
        citations = []
        if result.citations:
            for cit in result.citations:
                if isinstance(cit, dict):
                    citations.append(cit)

        # Send final result
        await websocket.send_json(
            {
                "type": "final_result",
                "data": {
                    "answer": result.answer,
                    "summary": getattr(result, "summary", ""),
                    "confidence": getattr(result, "confidence", "medium"),
                    "citations": citations,
                    "hops": result.hops or [],
                    "metadata": result.metadata or {},
                    "queries_used": result.metadata.get("queries_used", [])
                    if result.metadata
                    else [],
                    "final_reflection_reasoning": getattr(
                        result, "final_reflection_reasoning", None
                    ),
                },
            }
        )

        logger.info(f"🔍 Search complete: {session_id}")

    except WebSocketDisconnect:
        logger.info(f"🔍 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"🔴 WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(e),
                }
            )
        except Exception:
            pass  # WebSocket may already be closed


# =============================================================================
# Master Agent Widget Generation Endpoint
# =============================================================================


@router.websocket("/ws/generate-widget")
async def generate_widget_master_agent(websocket: WebSocket) -> None:
    """WebSocket endpoint for Master Agent widget generation with streaming.

    This endpoint implements the complete R014 Master-Agent pipeline:
    1. ANALYST (Pass 1): Understand query and context
    2. RESEARCHER: Fetch live data via SearXNG
    3. DATA CONTEXTUALIZER: Rerank, filter, contextualize
    4. ANALYST (Pass 2): Judge data quality (loop back if needed)
    5. DESIGNER: Add POVs, color schemes, visual hierarchy
    6. WIDGET SELECTOR: Choose widgets based on designed data
    7. SEQUENCER: Plan delivery order and timing
    8. PRESENTER: Final polish and QA
    9. HYDRATORS: Fill widgets with data (parallel)
    10. STAGGERED DELIVERY: Send widgets with 2-5s pacing

    Sends events in real-time:
    - qa_progress: QA checkpoint status (running, passed, failed)
    - widget: Individual widget as it passes QA
    - complete: Final delivery plan and QA report

    Client should send:
    {"query": "your question", "device_context": {...}}
    """
    await websocket.accept()
    session_id = str(uuid.uuid4())

    logger.info(f"🎯 Master Agent WebSocket connected: {session_id}")

    try:
        # Receive initial request
        data = await websocket.receive_json()

        user_query = data.get("query", "")
        device_context_raw = data.get("device_context", "desktop")
        # Handle both string and object formats for device_context
        if isinstance(device_context_raw, str):
            device_context = device_context_raw
        elif isinstance(device_context_raw, dict):
            device_context = device_context_raw.get("type", "desktop")
        else:
            device_context = "desktop"

        logger.info(
            f"🎯 Master Agent request: query='{user_query[:50]}...', "
            f"device={device_context}"
        )

        # Widget callback for staggered delivery
        async def send_widget(widget: dict, delay: float) -> None:
            """Send a single widget to the frontend with delay."""
            await asyncio.sleep(delay)
            await websocket.send_json(
                {
                    "type": "widget",
                    "data": widget,
                }
            )
            logger.info(f"📦 Widget sent: {widget.get('type', 'unknown')}")

        # QA progress callback
        async def send_qa_progress(checkpoint: str, status: str, data: dict) -> None:
            """Send QA checkpoint progress to frontend."""
            await websocket.send_json(
                {
                    "type": "qa_progress",
                    "data": {
                        "checkpoint": checkpoint,
                        "status": status,
                        "details": data,
                    },
                }
            )
            logger.info(f"✓ QA {checkpoint}: {status}")

        # Initialize all pipeline agents
        analyst = AnalystAgent()
        researcher = ResearcherAgent(searxng_url=settings.searxng_url)
        data_contextualizer = DataContextualizerAgent()
        designer = DesignerAgent()
        widget_selector = WidgetSelectorAgent()
        sequencer = SequencerAgent()
        presenter = PresenterAgent()

        # Initialize all hydrators
        hydrators = [
            ChartHydrator(),
            MarkdownHydrator(),
            CardHydrator(),
            FormHydrator(),
            ImageHydrator(),
            GalleryHydrator(),
        ]

        # Create master agent with callbacks
        master_agent = create_master_agent(
            widget_callback=send_widget,
            qa_callback=send_qa_progress,
        )

        # Set pipeline agents
        master_agent.set_pipeline_agents(
            analyst=analyst,
            researcher=researcher,
            data_contextualizer=data_contextualizer,
            designer=designer,
            widget_selector=widget_selector,
            sequencer=sequencer,
            presenter=presenter,
            hydrators=hydrators,
        )

        # Execute master agent with streaming
        delivery_plan: DeliveryPlan = await master_agent.execute_with_streaming(
            user_query=user_query,
            device_context=device_context,
        )

        # Send final completion message
        await websocket.send_json(
            {
                "type": "complete",
                "data": {
                    "delivery_plan": delivery_plan.model_dump()
                    if hasattr(delivery_plan, "model_dump")
                    else delivery_plan,
                },
            }
        )

        logger.info(f"🎯 Master Agent complete: {session_id}")

    except WebSocketDisconnect:
        logger.info(f"🎯 WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"🎯 Master Agent error: {e}", exc_info=True)
        try:
            await websocket.send_json(
                {
                    "type": "error",
                    "message": str(e),
                }
            )
        except Exception:
            pass  # WebSocket may already be closed
