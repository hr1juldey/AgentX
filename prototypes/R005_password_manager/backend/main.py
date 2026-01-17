"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config.settings import settings

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="A secure password manager with authentication and encryption",
    version="1.0.0",
    debug=settings.debug,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login",
            },
            "passwords": {
                "list": "GET /passwords",
                "create": "POST /passwords",
                "get": "GET /passwords/{id}",
                "update": "PUT /passwords/{id}",
                "delete": "DELETE /passwords/{id}",
            },
        },
    }


@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
    )
