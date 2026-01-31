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
from agentx.presentation.api.v1.thread_routes import router as thread_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    settings = get_settings()
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
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

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3015", "http://127.0.0.1:3015"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health_router, prefix="/api/v1", tags=["health"])
    app.include_router(agent_router, prefix="/api/v1/agent", tags=["agent"])
    app.include_router(thread_router, prefix="/api/v1/threads", tags=["threads"])

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
