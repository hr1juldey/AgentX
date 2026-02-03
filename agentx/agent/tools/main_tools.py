"""Main tools for DSPy ReAct agent.

Provides tool functions wrapped as dspy.Tool instances for use
with dspy.ReAct. These tools enable the agent to generate UI
descriptors and interact with various services.

Locked from LLD: agent_runtime.md:260-346
"""

from agentx.agent.tools.memory_tools import (
    categorize_memory,
    consolidate_memories,
    set_memory_ttl,
)
from agentx.agent.tools.ui_tools import (
    render_card,
    render_markdown_block,
    request_confirmation,
    show_chart,
    show_form,
    show_gallery,
    show_image,
    update_progress,
)

import dspy


AVAILABLE_TOOLS = [
    dspy.Tool(render_markdown_block, name="render_markdown_block"),
    dspy.Tool(render_card, name="render_card"),
    dspy.Tool(request_confirmation, name="request_confirmation"),
    dspy.Tool(update_progress, name="update_progress"),
    dspy.Tool(show_form, name="show_form"),
    dspy.Tool(show_image, name="show_image"),
    dspy.Tool(show_gallery, name="show_gallery"),
    dspy.Tool(show_chart, name="show_chart"),
    # Memory management tools (Mem0 for management, NOT retrieval)
    dspy.Tool(consolidate_memories, name="consolidate_memories"),
    dspy.Tool(categorize_memory, name="categorize_memory"),
    dspy.Tool(set_memory_ttl, name="set_memory_ttl"),
]
