"""DSPy signatures for reasoning tasks."""

import dspy


class ReasoningSignature(dspy.Signature):
    """Signature for general reasoning tasks.

    The pluripotent stem cell signature - handles general queries.
    """

    context: str = dspy.InputField(desc="Background context")
    question: str = dspy.InputField(desc="The question to answer")

    answer: str = dspy.OutputField(desc="The answer to the question")
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning")
