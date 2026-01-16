"""Main application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pathlib import Path

from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO if settings.debug else logging.WARNING)
logger = logging.getLogger(__name__)

# Create upload directory
settings.upload_dir.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name, version=settings.version, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes import router
app.include_router(router)


@app.get("/")
async def root():
    return {"service": settings.app_name, "version": settings.version, "status": "running", "endpoints": {"/docs": "API docs", "/health": "Health check"}}


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=settings.debug)
