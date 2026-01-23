# =============================================================================
# AGENTX Researcher Tools Package
# =============================================================================
# DSPy modules and services for the RESEARCHER agent
# =============================================================================

from services.tools.researcher.citation_builder import (
    CitationBuilderModule,
)
from services.tools.researcher.content_filter import (
    ContentFilterModule,
)
from services.tools.researcher.data_processor import (
    BeautifierModule,
    DataStructurerModule,
)
from services.tools.researcher.multihop_reader import (
    MultiHopReader,
)
from services.tools.researcher.report_generator import (
    ReportGeneratorModule,
)
from services.tools.researcher.searxng_search import (
    SearXNGSearchModule,
)
from services.tools.researcher.web_fetcher import (
    fetch_page,
    fetch_multiple_pages,
    truncate_content,
)

__all__ = [
    # DSPy Modules
    "SearXNGSearchModule",
    "BeautifierModule",
    "DataStructurerModule",
    "CitationBuilderModule",
    "ContentFilterModule",
    "ReportGeneratorModule",
    # Multi-hop Reader (orchestrator, not DSPy)
    "MultiHopReader",
    # Pure functions (web_fetcher)
    "fetch_page",
    "fetch_multiple_pages",
    "truncate_content",
]
