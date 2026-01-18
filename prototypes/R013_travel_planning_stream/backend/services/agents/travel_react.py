# =============================================================================
# AGENTX R013 - Travel ReAct Agent with Streaming Support
# =============================================================================
# ReAct agent with dspy.streamify for real-time token streaming
# =============================================================================

import logging
from typing import Any

import dspy
from services.search_service import search_travel_sync

logger = logging.getLogger(__name__)


# Define simple signature for question answering with conversation history
class TravelQuestion(dspy.Signature):
    """Answer travel questions with conversation memory."""

    question = dspy.InputField(desc="User's travel question")
    history: dspy.History = dspy.InputField(desc="Conversation history")
    answer = dspy.OutputField(desc="Helpful travel response")


class TravelAgentReAct(dspy.Module):
    """ReAct agent with streaming support for travel planning.

    CRITICAL: This implementation follows DSPy's async/streamify best practices:
    1. Sync warmup before async operations
    2. dspy.streamify with allow_reuse=True for ReAct loops
    3. Proper acall() usage for async execution
    """

    def __init__(self, max_steps: int = 5):
        """Initialize ReAct agent with specialized tools.

        Args:
            max_steps: Maximum number of reasoning steps
        """
        super().__init__()
        self.max_steps = max_steps

        # Define tools - using synchronous wrapper with explicit dspy.Tool
        # The Tool wrapper provides better documentation to prevent argument hallucination
        def search_travel(query: str) -> str:
            """Search for current travel information.

            Args:
                query: Search query string (e.g., "top places to visit in India")

            Returns:
                Contextualized search results as string

            Note:
                This function accepts ONLY a 'query' argument. Do not pass
                any other arguments like 'places', 'destinations', etc.
            """
            return search_travel_sync(query)

        # Wrap with dspy.Tool for better LLM understanding of the interface
        search_tool = dspy.Tool(
            search_travel,
            name="search_travel",
            desc="Search for current travel information. Accepts a single 'query' string argument.",
        )

        # Create ReAct program with tools
        react_program = dspy.ReAct(
            TravelQuestion,
            tools=[search_tool],
        )
        self.react = react_program

        # Streaming wrapper (initialized but not warmed up yet)
        # Type: dspy.streamify returns a complex callable type, not dspy.Module
        self._stream_react: Any | None = None
        self._warmed_up = False

    def warmup(self) -> None:
        """Synchronous warmup to initialize DSPy internal state.

        CRITICAL: Call this BEFORE using async streaming to avoid
        first-call initialization issues with streamify.

        This is the "sync warmup" pattern required by DSPy's streamify.
        """
        if self._warmed_up:
            return

        logger.info("Performing synchronous warmup for ReAct agent...")

        # Create streamify wrapper with allow_reuse for ReAct loops
        logger.info("Creating streamify wrapper with StreamListener...")
        self._stream_react = dspy.streamify(
            self.react,
            stream_listeners=[
                dspy.streaming.StreamListener(
                    signature_field_name="next_thought",
                    allow_reuse=True,
                )
            ],
        )

        # CRITICAL: Sync warmup call to initialize StreamListener state
        # This ensures stream_start flag is set and internal state is ready
        logger.info("Calling ReAct with warmup question (sync)...")
        try:
            _ = self.react(question="warmup", history=dspy.History(messages=[]))
            logger.info("ReAct agent sync warmup complete")
        except Exception as e:
            logger.warning(f"ReAct warmup had issues: {e}")

        self._warmed_up = True

    def get_streamer(self) -> Any:
        """Get the streamified ReAct agent.

        Returns:
            Streamified ReAct callable ready for async iteration

        Raises:
            RuntimeError: If warmup() was not called first
        """
        if not self._warmed_up or self._stream_react is None:
            raise RuntimeError(
                "Must call warmup() before using streaming. "
                "This is required by DSPy's streamify to initialize "
                "StreamListener state properly."
            )
        return self._stream_react

    def forward(
        self, question: str, history: dspy.History | None = None
    ) -> dspy.Prediction:
        """Process question using ReAct (synchronous mode).

        Args:
            question: User's travel question
            history: Optional conversation history

        Returns:
            Prediction with answer
        """
        if history is None:
            history = dspy.History(messages=[])
        result = self.react(question=question, history=history)
        assert isinstance(result, dspy.Prediction)
        return result
