"""DSPy signatures for Real AgentX v0.1.

Defines the input/output signatures for DSPy modules.
Following DSPy tutorial patterns from /home/riju279/Downloads/dspy-main/dspy-main/docs/
"""

import dspy


class MainAgentSignature(dspy.Signature):
    """Main agent signature for query processing.

    Maps user queries to agent responses with tool support.
    """

    query = dspy.InputField(desc="User's question or request")
    context = dspy.InputField(desc="Relevant context from memory or tools", default="")
    response = dspy.OutputField(desc="Agent's response to the user")
    reasoning = dspy.OutputField(desc="Step-by-step reasoning process")


class AnalystSignature(dspy.Signature):
    """Analyst agent signature for query understanding.

    Analyzes user queries to extract intent and entities.
    """

    query = dspy.InputField(desc="User's question or request")
    intent = dspy.OutputField(desc="Detected user intent")
    entities = dspy.OutputField(desc="Extracted entities and parameters")
    tool_needed = dspy.OutputField(desc="Whether a tool is needed (yes/no)")
    tool_name = dspy.OutputField(desc="Name of the tool if needed")


class DesignerSignature(dspy.Signature):
    """Designer agent signature for UI widget selection.

    Selects appropriate UI components based on query and context.
    Server-driven UI pattern from C007.
    """

    query = dspy.InputField(desc="User's question or request")
    response = dspy.InputField(desc="Agent's response content")
    existing_widgets = dspy.InputField(
        desc="List of already shown widget types",
        default=list,
    )
    recommended_widget = dspy.OutputField(desc="Recommended UI widget type")
    widget_props = dspy.OutputField(desc="Widget properties as JSON")


class MemorySignature(dspy.Signature):
    """Memory agent signature for RAG operations.

    Retrieves relevant context from memory stores.
    """

    query = dspy.InputField(desc="User's question or request")
    session_id = dspy.InputField(desc="Current session identifier")
    context = dspy.OutputField(desc="Relevant context from memory")
    sources = dspy.OutputField(desc="Source references for retrieved context")


class ToolExecutorSignature(dspy.Signature):
    """Tool executor signature for tool execution.

    Executes tools with validated parameters.
    """

    tool_name = dspy.InputField(desc="Name of the tool to execute")
    parameters = dspy.InputField(desc="Tool parameters as JSON")
    result = dspy.OutputField(desc="Tool execution result")
    error = dspy.OutputField(desc="Error message if execution failed", default="")
