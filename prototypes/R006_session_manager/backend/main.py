"""Main application entry point."""
import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint with service information."""
    return {
        "service": settings.app_name,
        "version": settings.version,
        "status": "running",
        "endpoints": {
            "sessions": "/sessions",
            "storage_status": "/sessions/status/storage",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    from services.service import session_service

    storage_status = session_service.get_storage_status()
    return {
        "status": "healthy",
        "storage": storage_status.get("storage_type", "unknown"),
        "storage_warning": storage_status.get("warning"),
    }


if __name__ == "__main__":
    from services.service import session_service

    logger.info(f"🚀 Starting {settings.app_name} v{settings.version}")
    logger.info(f"📡 Server will be available at http://localhost:{settings.port}")
    logger.info(f"📚 API documentation at http://localhost:{settings.port}/docs")

    # Check storage status on startup
    storage_status = session_service.get_storage_status()
    logger.info(f"💾 Storage: {storage_status['storage_type']}")
    if "warning" in storage_status:
        logger.warning(f"⚠️  {storage_status['warning']}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
