# =============================================================================
# AGENTX R013 - DSPy Service
# =============================================================================
# DSPy LM configuration and warmup for travel planning
# =============================================================================

import logging
from datetime import datetime

import dspy

from config.settings import settings

logger = logging.getLogger(__name__)


# Signature for warmup questions
class WarmupQuestion(dspy.Signature):
    """Simple question-answer for warmup."""

    question = dspy.InputField(desc="Question to answer")
    answer = dspy.OutputField(desc="Answer to the question")


class DSPyService:
    """DSPy service for LLM configuration and warmup.

    CRITICAL: Warmup is SYNCHRONOUS by design.
    DSPy requires sync warmup to initialize internal state before
    async operations (acall/streamify) can work properly.
    """

    def __init__(self) -> None:
        """Initialize DSPy with Ollama gemma3:4b."""
        # Select LM configuration based on llm_mode
        if settings.llm_mode == "openai_compatible":
            self.lm = dspy.LM(
                model=settings.ollama_openai_model,
                api_base=settings.ollama_openai_base_url,
                api_key=settings.ollama_openai_api_key,
                model_type="chat",
                cache=False,
                num_retries=2,
                async_max_workers=settings.async_max_workers,
            )
            logger.info(
                f"DSPy configured with OpenAI-compatible mode: {settings.ollama_openai_model}"
            )
        else:
            # Native mode (default)
            self.lm = dspy.LM(
                model=settings.llm_model,
                api_base=settings.ollama_base_url,
                api_key="",
                cache=False,
                num_retries=2,
                async_max_workers=settings.async_max_workers,
            )
            logger.info(f"DSPy configured with native mode: {settings.llm_model}")

        dspy.configure(lm=self.lm)

    def warmup(self) -> None:
        """SYNCHRONOUS warmup for LLM initialization.

        This is intentionally synchronous (not async) because:
        1. DSPy requires sync warmup to initialize StreamListener state
        2. First call compiles signatures and sets up internal structures
        3. Async operations (acall, streamify) depend on this initialization

        After warmup completes, you can use async operations:
        - Use .acall() for async execution
        - Use dspy.streamify() for token streaming
        """
        logger.info("Starting LLM warmup (synchronous)...")

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%Y-%m-%d")

        # Time-based QA to prevent cached replies
        warmup_questions = [
            f"The current time is {current_time} on {current_date}. What time will it be in 1 hour?",
            f"The current time is {current_time} on {current_date}. What time will it be in 30 minutes?",
            f"The current date is {current_date}. What will be the date 7 days from now?",
            f"The current time is {current_time}. What time was it 2 hours ago?",
        ]

        # Create DSPy predictor for warmup (SYNCHRONOUS call)
        warmup_predict = dspy.Predict(WarmupQuestion)

        for i, q in enumerate(warmup_questions, 1):
            try:
                logger.info(f"Warmup {i}/4: Calling LLM...")
                result = warmup_predict(question=q)  # Sync call - actually invokes LLM
                answer_text = (
                    str(result.answer) if hasattr(result, "answer") else str(result)
                )
                logger.info(f"Warmup {i}/4: Got response - {answer_text[:200]}...")
            except Exception as e:
                logger.warning(f"Warmup question {i} failed: {e}")

        logger.info("LLM warmup complete (async operations now ready)")


# Singleton instance
dspy_service = DSPyService()
