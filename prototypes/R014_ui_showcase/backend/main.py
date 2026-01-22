# =============================================================================
# AGENTX Prototype - FastAPI Main Application
# =============================================================================
# Minimal FastAPI app template for prototype development
# =============================================================================

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import settings

# Configure DEBUG logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.debug(f"🚀 {settings.app_name} v{settings.app_version} starting...")
    logger.debug(f"Debug mode: {settings.debug}")
    logger.debug(f"LLM Provider: {settings.llm_provider}, Model: {settings.llm_model}")
    yield
    # Shutdown
    logger.debug(f"👋 {settings.app_name} shutting down...")


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


def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        reload_excludes=["tests/*", "tests/*.*", ".pytest_cache/*", "*.pyc"],
    )


if __name__ == "__main__":
    main()
