# =============================================================================
# AGENTX R014 - Application Layer - Response DTOs
# =============================================================================
# Data Transfer Objects for API responses (Clean Architecture)
# =============================================================================


from pydantic import BaseModel

# Import domain entity for use in responses
from domain.entities.ui_descriptor import UIDescriptor


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    llm: dict[str, str]


# Response DTOs can use domain entities directly
UIDescriptorResponse = UIDescriptor
