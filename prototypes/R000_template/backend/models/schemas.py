# =============================================================================
# AGENTX Prototype - Pydantic Models
# =============================================================================
# Request/response schemas for API endpoints
# =============================================================================

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Service status")
    app: str = Field(description="Application name")
    version: str = Field(description="Application version")


class ItemCreate(BaseModel):
    """Schema for creating an item (example)."""

    name: str = Field(..., description="Item name", min_length=1, max_length=100)
    description: str | None = Field(None, description="Item description")


class ItemResponse(ItemCreate):
    """Schema for item response."""

    id: int = Field(..., description="Item ID")
    created_at: str = Field(..., description="Creation timestamp")


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Detailed error information")
