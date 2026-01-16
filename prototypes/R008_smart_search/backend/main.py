"""Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from config.settings import settings
from api.routes import router

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
            "search": "/search",
            "documents": "/documents",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Health check endpoint."""
    from services.service import search_service
    info = await search_service.get_collection_info()
    return {
        "status": "healthy",
        "qdrant_connected": info["connected"],
        "collection_exists": info["collection_exists"],
    }


if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Server will be available at http://localhost:{settings.port}")
    logger.info(f"API documentation at http://localhost:{settings.port}/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info",
    )
