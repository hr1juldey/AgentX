# =============================================================================
# AGENTX Tools Package
# =============================================================================
# DSPy module tools for specialist agents
# =============================================================================

from services.tools.analyst import (
    ContextAnalyzerModule,
    DataQualityCheckerModule,
    GoalDetectorModule,
    InsightExtractorModule,
)
from services.tools.contextualizer import (
    ContextualizerModule,
    FilterModule,
    RerankerModule,
)
from services.tools.designer import (
    AccessibilityModule,
    ColorPickerModule,
    HierarchyPlannerModule,
    POVGeneratorModule,
)
from services.tools.hydrators import (
    CardHydratorModule,
    ChartHydratorModule,
    FormHydratorModule,
    GalleryHydratorModule,
    ImageHydratorModule,
    MarkdownHydratorModule,
)
from services.tools.presenter import (
    FlowCheckerModule,
    PolisherModule,
    QAFinalizerModule,
)
from services.tools.researcher import (
    BeautifierModule,
    CitationBuilderModule,
    DataStructurerModule,
    SearXNGSearchModule,
)
from services.tools.selector_tools import (
    WidgetMatcherModule,
)
from services.tools.sequencing_tools import (
    FlowPlannerModule,
    PacingCalculatorModule,
)

__all__ = [
    # Analyst Tools
    "ContextAnalyzerModule",
    "InsightExtractorModule",
    "GoalDetectorModule",
    "DataQualityCheckerModule",
    # Research Tools
    "SearXNGSearchModule",
    "BeautifierModule",
    "DataStructurerModule",
    "CitationBuilderModule",
    # Contextualizer Tools
    "RerankerModule",
    "FilterModule",
    "ContextualizerModule",
    # Designer Tools
    "POVGeneratorModule",
    "ColorPickerModule",
    "HierarchyPlannerModule",
    "AccessibilityModule",
    # Selector Tools
    "WidgetMatcherModule",
    # Sequencer Tools
    "FlowPlannerModule",
    "PacingCalculatorModule",
    # Presenter Tools
    "FlowCheckerModule",
    "PolisherModule",
    "QAFinalizerModule",
    # Hydration Tools
    "ChartHydratorModule",
    "MarkdownHydratorModule",
    "CardHydratorModule",
    "FormHydratorModule",
    "ImageHydratorModule",
    "GalleryHydratorModule",
]
