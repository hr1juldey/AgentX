"""AGENTX Main Application Entry Point.

FastAPI factory with lifespan management for DSPy, Mem0AI, Qdrant, etc.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agentx.core.config import settings
from agentx.core.dependencies import ensure_dspy_configured
from agentx.presentation.api.v1.agents.routes import router as agents_router
from agentx.presentation.api.v1.graphs.routes import router as graphs_router
from agentx.presentation.api.v1.memory.routes import router as memory_router
from agentx.presentation.api.v1.threads.routes import router as threads_router
from agentx.presentation.api.v1.voice.routes import router as voice_router
from agentx.presentation.api.v1.websocket.routes import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    print("Starting AGENTX...")

    # Configure DSPy globally
    try:
        ensure_dspy_configured()
        print("DSPy configured successfully")
    except NotImplementedError as e:
        print(f"Warning: {e}")

    # TODO: Initialize Mem0AI client
    # TODO: Initialize Qdrant client
    # TODO: Initialize voice clients

    yield

    # Shutdown
    print("Shutting down AGENTX...")
    # TODO: Cleanup connections


def create_app() -> FastAPI:
    """Create FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="AGENTX",
        description="Personal AI Assistant Framework",
        version="0.1.0",
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

    # Include API routers (new structure)
    app.include_router(agents_router, prefix="/api/v1")
    app.include_router(graphs_router, prefix="/api/v1")
    app.include_router(memory_router, prefix="/api/v1")
    app.include_router(voice_router, prefix="/api/v1")
    app.include_router(threads_router, prefix="/api/v1")
    app.include_router(websocket_router, prefix="/api/v1")

    @app.get("/")
    async def root() -> dict:
        """Root endpoint.

        Returns:
            Welcome message
        """
        return {"message": "AGENTX - Personal AI Assistant Framework"}

    @app.get("/health")
    async def health() -> dict:
        """Health check endpoint.

        Returns:
            Health status
        """
        return {"status": "healthy"}

    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agentx.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
