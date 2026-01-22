# =============================================================================
# AGENTX R014 - API Models (DEPRECATED - Use Domain Entities)
# =============================================================================
# ⚠️  DEPRECATED: This file is maintained for backward compatibility.
# New code should import from:
#   - domain.entities (for domain entities like UIDescriptor)
#   - application.dtos.requests (for request DTOs)
# =============================================================================

# Deprecated aliases - import from domain layer
from application.dtos.requests import (
    GenerateWidgetRequest as GenerateRequest,
    IntelligentGenerateRequest,
)
from domain.entities.ui_descriptor import UIDescriptor as UIDescriptorEntity

# Maintain backward compatibility by re-exporting with old names
__all__ = [
    "UIDescriptor",
    "GenerateRequest",
    "IntelligentGenerateRequest",
]

# Type aliases for backward compatibility
UIDescriptor = UIDescriptorEntity
