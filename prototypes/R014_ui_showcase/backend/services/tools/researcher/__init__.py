# =============================================================================
# AGENTX Researcher Tools Package
# =============================================================================
# DSPy modules for the RESEARCHER agent
# =============================================================================

from services.tools.researcher.citation_builder import (
    CitationBuilderModule,
)
from services.tools.researcher.data_processor import (
    BeautifierModule,
    DataStructurerModule,
)
from services.tools.researcher.searxng_search import (
    SearXNGSearchModule,
)

__all__ = [
    "SearXNGSearchModule",
    "BeautifierModule",
    "DataStructurerModule",
    "CitationBuilderModule",
]
