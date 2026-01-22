# =============================================================================
# AGENTX Widget Spawner - Layouts Package
# =============================================================================
# Layout strategies for intelligent widget positioning
# =============================================================================

from services.widget_spawner.layouts.grid import (
    generate_grid_2column_layout,
    generate_grid_3column_layout,
)
from services.widget_spawner.layouts.masonry import (
    generate_default_layout,
    generate_masonry_layout,
)
from services.widget_spawner.layouts.vertical import generate_vertical_layout

__all__ = [
    "generate_vertical_layout",
    "generate_grid_2column_layout",
    "generate_grid_3column_layout",
    "generate_masonry_layout",
    "generate_default_layout",
]
