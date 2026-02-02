"""Real AgentX v0.1 - Main entry point.

FastAPI application factory following the pattern from mimicus.
Creates and configures the ASGI application with all routes and middleware.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentx.core.config import get_settings
from agentx.presentation.api.v1.agent_routes import router as agent_router
from agentx.presentation.api.v1.health import router as health_router
from agentx.presentation.api.v1.memory_routes import router as memory_router
from agentx.presentation.api.v1.thread_routes import router as thread_router
from agentx.presentation.api.v1.voice_routes import router as voice_router
from agentx.presentation.api.v1.websocket_routes import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"LLM: {settings.llm.provider}/{settings.llm.model}")

    # Configure DSPy with Ollama
    from agentx.core.dependencies import ensure_dspy_configured

    ensure_dspy_configured()
    print("DSPy configured successfully")

    # Initialize LangGraph Redis connections
    from agentx.infrastructure.memory.redis_lifespan import redis_lifespan

    DB_URI = "redis://localhost:6380"
    async with redis_lifespan(DB_URI):
        print("LangGraph Redis connections initialized")
        yield

    # Shutdown
    print("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: The configured application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS middleware - allow frontend, network IP, and kyutai voice-server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3015",
            "http://127.0.0.1:3015",
            "http://192.168.1.4:3015",
            "http://localhost:16000",  # Kyutai voice-server
            "ws://localhost:16000",  # Kyutai WebSocket
            "http://192.168.1.4:16000",  # Kyutai network access
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent"])
    app.include_router(thread_router, prefix="/api/v1/threads", tags=["threads"])
    app.include_router(websocket_router, prefix="/api/v1", tags=["websocket"])
    app.include_router(memory_router, prefix="/api/v1/memory", tags=["memory"])
    app.include_router(voice_router)  # Already has prefix="/api/v1/voice" in definition

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "agentx.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.debug,
        log_level=settings.server.log_level,
    )
