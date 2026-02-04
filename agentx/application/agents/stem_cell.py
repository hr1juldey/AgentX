"""Stem Cell Agent - pluripotent base agent for AGENTX.

The StemCellAgent is the foundation from which all specialized agents differentiate.
It uses signature-based differentiation as the primary mechanism.
"""

from typing import Optional

import dspy


class StemCellAgent(dspy.Module):
    """Pluripotent stem cell agent for AGENTX.

    Can differentiate into specialized agent types via signature changes.
    Uses global DSPy LM/RM and per-agent Mem0AI for user-scoped memory.

    Attributes:
        user_id: User identifier for memory isolation
        mem0_user_id: Same as user_id, passed to Mem0AI
        signature: Current DSPy signature
    """

    def __init__(
        self,
        user_id: str,
        signature: Optional[dspy.Signature] = None,
        enable_tools: bool = False,
    ) -> None:
        """Initialize the stem cell agent.

        Args:
            user_id: User identifier for memory isolation
            signature: Optional DSPy signature (default: pluripotent reasoning signature)
            enable_tools: Whether to enable tool mounting
        """
        super().__init__()

        self.user_id = user_id
        self.mem0_user_id = user_id
        self.enable_tools = enable_tools

        # Set signature (default pluripotent if not provided)
        if signature is None:
            from agentx.domain.signatures.reasoning_signature import ReasoningSignature

            self.signature = ReasoningSignature
        else:
            self.signature = signature  # type: ignore[assignment]

        # Initialize reasoning module with current signature
        self.reasoning = dspy.ChainOfThought(self.signature)

        # DSPy History for conversation context (shared across all signatures)
        self._history: dspy.History = dspy.History(messages=[])

        # Memory client (singleton)
        self._mem0_client: Optional[object] = None
        self._tools: list[dspy.Tool] = []

    def set_signature(self, signature: dspy.Signature) -> None:
        """Change the agent's signature.

        Args:
            signature: New DSPy signature to use
        """
        raise NotImplementedError("Signature switching not yet implemented")

    def reset_signature(self) -> None:
        """Reset to default pluripotent signature."""
        raise NotImplementedError("Signature reset not yet implemented")

    def add_tool(self, tool: dspy.Tool) -> None:
        """Mount a tool to this agent.

        Args:
            tool: DSPy Tool to mount
        """
        raise NotImplementedError("Tool mounting not yet implemented")

    def forward(
        self, context: str = "", question: str = "", **kwargs: object
    ) -> dspy.Prediction:
        """Execute the agent with history management.

        Args:
            context: Background context (for pluripotent signature)
            question: The input question
            **kwargs: Additional arguments (e.g., history for conversation signature)

        Returns:
            DSPy Prediction with results
        """
        # Step 1: Prepare inputs for reasoning module
        reasoning_inputs: dict[str, object] = {"question": question}

        # Add context if provided (for pluripotent ReasoningSignature)
        if context:
            reasoning_inputs["context"] = context

        # Add history if signature supports it (for ConversationSignature)
        # Check if signature expects a "history" input field
        sig_inputs = self.signature.input_fields
        if "history" in sig_inputs:
            reasoning_inputs["history"] = self._history

        # Step 2: Execute reasoning
        result = self.reasoning(**reasoning_inputs)

        # Step 3: Append to DSPy history for context in next turn
        # DSPy Prediction is dict-like; extract fields for storage
        self._history.messages.append({"question": question, **dict(result)})  # type: ignore[no-matching-overload]

        return result  # type: ignore[bad-return]
