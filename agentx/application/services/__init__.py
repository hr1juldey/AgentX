"""Application services for AGENTX.

Re-exports all domain services for backward compatibility.
"""

# Orchestration
from agentx.application.services.orchestration import (
    AgentOrchestrator,
    UIService,
    RoutingDecisionService,
)

# RAG Conflict
from agentx.application.services.rag_conflict import (
    RAGConflictResolver,
    ConflictResolutionResult,
)

# Search Strategy
from agentx.application.services.search_strategy import HybridSearchService

# Search Patterns
from agentx.application.services.search_patterns import SearchTermPatternService

# Synthesis
from agentx.application.services.synthesis import SynthesisService

# Existing domains
from agentx.application.services.temporal_rag import TemporalRAGService
from agentx.application.services.duration import DurationMemoryService

__all__ = [
    "AgentOrchestrator",
    "UIService",
    "RoutingDecisionService",
    "RAGConflictResolver",
    "ConflictResolutionResult",
    "HybridSearchService",
    "SearchTermPatternService",
    "SynthesisService",
    "TemporalRAGService",
    "DurationMemoryService",
]
