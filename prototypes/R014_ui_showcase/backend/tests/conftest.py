# =============================================================================
# AGENTX R014 - Global Test Fixtures (Real API, No Mocks)
# =============================================================================

import logging

import pytest
from fastapi.testclient import TestClient

from main import app
from config.dspy import configure_dspy, get_lm_info
from config.settings import settings


# =============================================================================
# Logging Setup
# =============================================================================

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# =============================================================================
# DSPy Configuration Fixture (REAL Ollama LM)
# =============================================================================


@pytest.fixture(scope="session")
def configure_test_dspy():
    """Configure DSPy with REAL Ollama LM (same as production).

    CRITICAL: This uses the actual Ollama backend, not a mock.
    Uses qwen3:8b model for testing (same as production).

    Ensure Ollama is running: `ollama serve`
    Ensure model is pulled: `ollama pull qwen3:8b`
    """
    logger.info("Configuring DSPy with REAL Ollama LM (qwen3:8b) for tests...")
    # Override model for tests
    import os

    os.environ["LLM_MODEL"] = "qwen3:8b"
    configure_dspy()
    lm_info = get_lm_info()
    logger.info(f"DSPy configured: {lm_info}")
    return lm_info


# =============================================================================
# Real API Client Fixtures
# =============================================================================


@pytest.fixture
def api_client() -> TestClient:
    """FastAPI TestClient for REAL REST API testing."""
    return TestClient(app)


@pytest.fixture
def api_base_url() -> str:
    """Base URL for API endpoints."""
    return "/api/v1"


# =============================================================================
# Real Pipeline Agent Fixtures (NOT mocked)
# =============================================================================


@pytest.fixture
def real_analyst_agent(configure_test_dspy):
    """Real ANALYST agent (uses real DSPy)."""
    from services.pipeline.analyst import AnalystAgent

    return AnalystAgent()


@pytest.fixture
def real_researcher_agent():
    """Real RESEARCHER agent (uses real SearXNG)."""
    from services.pipeline.researcher import ResearcherAgent

    return ResearcherAgent(searxng_url=settings.searxng_url)


@pytest.fixture
def real_data_contextualizer_agent(configure_test_dspy):
    """Real DATA CONTEXTUALIZER agent (uses real DSPy)."""
    from services.pipeline.data_contextualizer import DataContextualizerAgent

    return DataContextualizerAgent()


@pytest.fixture
def real_designer_agent(configure_test_dspy):
    """Real DESIGNER agent (uses real DSPy)."""
    from services.pipeline.designer import DesignerAgent

    return DesignerAgent()


@pytest.fixture
def real_widget_selector_agent(configure_test_dspy):
    """Real WIDGET SELECTOR agent (uses real DSPy)."""
    from services.pipeline.widget_selector import WidgetSelectorAgent

    return WidgetSelectorAgent()


@pytest.fixture
def real_sequencer_agent(configure_test_dspy):
    """Real SEQUENCER agent (uses real DSPy)."""
    from services.pipeline.sequencer import SequencerAgent

    return SequencerAgent()


@pytest.fixture
def real_presenter_agent(configure_test_dspy):
    """Real PRESENTER agent (uses real DSPy)."""
    from services.pipeline.presenter import PresenterAgent

    return PresenterAgent()


@pytest.fixture
def real_hydrators():
    """Real hydrators (no mocks)."""
    from services.hydrators.chart_hydrator import ChartHydrator
    from services.hydrators.markdown_hydrator import MarkdownHydrator
    from services.hydrators.card_hydrator import CardHydrator
    from services.hydrators.form_hydrator import FormHydrator
    from services.hydrators.image_hydrator import ImageHydrator
    from services.hydrators.gallery_hydrator import GalleryHydrator

    return [
        ChartHydrator(),
        MarkdownHydrator(),
        CardHydrator(),
        FormHydrator(),
        ImageHydrator(),
        GalleryHydrator(),
    ]


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_finance_queries():
    """Sample finance queries for testing."""
    return [
        "Global Inflation Trends (2015–Present)",
        "Interest Rate Hikes and Stock Market Volatility",
        "US Federal Reserve Balance Sheet Expansion vs Asset Prices",
        "Crude Oil Prices vs Geopolitical Conflicts",
        "Gold Prices During Economic Crises",
    ]


@pytest.fixture
def sample_world_events_queries():
    """Sample world events queries for testing."""
    return [
        "Economic Impact of Major Wars Since 2000",
        "Global Energy Mix Transition",
        "Sanctions and Their Effect on National Economies",
        "Food Price Index vs Climate Events",
        "Migration Flows Triggered by Economic Crises",
    ]


# =============================================================================
# Skip Conditions
# =============================================================================


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "websocket: marks tests as WebSocket tests")
    config.addinivalue_line("markers", "requires_ollama: marks tests requiring Ollama")
    config.addinivalue_line(
        "markers", "requires_searxng: marks tests requiring SearXNG"
    )


@pytest.fixture(autouse=True)
def skip_if_no_ollama(request):
    """Skip tests marked with 'requires_ollama' if Ollama is not available."""
    if request.node.get_closest_marker("requires_ollama"):
        import httpx

        try:
            response = httpx.get("http://localhost:11434/api/tags", timeout=2.0)
            if response.status_code != 200:
                pytest.skip("Ollama not available at http://localhost:11434")
        except Exception:
            pytest.skip("Ollama not available at http://localhost:11434")


@pytest.fixture(autouse=True)
def skip_if_no_searxng(request):
    """Skip tests marked with 'requires_searxng' if SearXNG is not available."""
    if request.node.get_closest_marker("requires_searxng"):
        import httpx

        try:
            response = httpx.get(settings.searxng_url, timeout=5.0)
            if response.status_code != 200:
                pytest.skip(f"SearXNG not available at {settings.searxng_url}")
        except Exception:
            pytest.skip(f"SearXNG not available at {settings.searxng_url}")
