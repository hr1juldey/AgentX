# =============================================================================
# AGENTX R013 - FastAPI Main Application
# =============================================================================
# FastAPI app with DSPy async + WebSocket streaming
# =============================================================================

import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.logging import StderrCapture, setup_logging
from config.settings import settings
from services.agents.travel_react import TravelAgentReAct
from services.dspy_service import dspy_service

# Initialize global ReAct agent (will be warmed up at startup)
travel_agent = TravelAgentReAct()

# Setup logging (includes Pydantic warning filter)
file_handler = setup_logging()
sys.stderr = StderrCapture(file_handler)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager with graceful shutdown."""
    # Startup
    logger.info(f"{settings.app_name} v{settings.app_version} starting...")
    print(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    print("Press Ctrl+C to shutdown gracefully")

    # CRITICAL: SYNCHRONOUS warmup for DSPy LLM
    # This initializes internal state before async operations
    # DSPy requires sync warmup to compile signatures and set up structures
    print("🔥 Warming up LLM (synchronous)...")
    dspy_service.warmup()  # No await - this is synchronous!
    print("✅ LLM warmup complete")

    # CRITICAL: Sync warmup for ReAct agent streamify
    # DSPy requires synchronous warmup BEFORE async streaming to initialize
    # StreamListener state and avoid first-call initialization issues
    print("🔥 Warming up ReAct agent for streaming...")
    travel_agent.warmup()  # Synchronous call - CRITICAL for streamify!
    print("✅ ReAct agent warmup complete - streaming ready")

    # Pass warmed-up agent to routes
    from api import routes

    routes.set_travel_agent(travel_agent)
    print("✅ Travel agent registered with routes")
    print("✅ All async operations (acall, streamify) now ready")

    yield
    # Shutdown - runs when app shuts down
    logger.info(f"{settings.app_name} shutting down...")
    print(f"👋 {settings.app_name} shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=f"{settings.app_name} API",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint for health check."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
