# =============================================================================
# AGENTX R014 - Application Layer - Response DTOs
# =============================================================================
# Data Transfer Objects for API responses (Clean Architecture)
# =============================================================================

from typing import Any

from pydantic import BaseModel

# Import domain entity for use in responses
from domain.entities.ui_descriptor import UIDescriptor


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    llm: dict[str, str]


class SearchResultResponse(BaseModel):
    """Final search result response."""

    answer: str
    summary: str = ""
    confidence: str = "medium"
    citations: list[dict[str, Any]] = []
    hops: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}
    queries_used: list[str] = []
    final_reflection_reasoning: str | None = None


# Response DTOs can use domain entities directly
UIDescriptorResponse = UIDescriptor
