# =============================================================================
# AGENTX Master Agent - Phase Executor
# =============================================================================
# Executes individual pipeline phases with QA checkpoints
# =============================================================================

import asyncio
import logging
from typing import Callable

from services.master_agent.qa_checkpoints import QACheckpointModule

logger = logging.getLogger(__name__)


class PhaseExecutor:
    """Executes individual pipeline phases with QA checkpoints."""

    def __init__(
        self,
        qa: QACheckpointModule,
        qa_callback: Callable | None = None,
    ) -> None:
        """Initialize phase executor.

        Args:
            qa: QA checkpoint module
            qa_callback: Optional callback for QA progress
        """
        self.qa = qa
        self.qa_callback = qa_callback

    def execute_phase(
        self,
        checkpoint_name: str,
        phase_func: Callable,
    ) -> dict:
        """Execute a single pipeline phase with QA checkpoint.

        Args:
            checkpoint_name: Name of the QA checkpoint
            phase_func: Function to execute for this phase

        Returns:
            Phase result data

        Raises:
            Exception: If phase execution fails
        """
        try:
            result = phase_func()
            self.qa.validate_checkpoint(checkpoint_name, result)
            self._emit_qa_progress(checkpoint_name, "passed", result)
            return result
        except Exception as e:
            self.qa.mark_failed(checkpoint_name, str(e))
            self._emit_qa_progress(checkpoint_name, "failed", {"error": str(e)})
            raise

    def _emit_qa_progress(
        self,
        checkpoint: str,
        status: str,
        data: dict,
    ) -> None:
        """Emit QA progress to frontend via callback.

        Args:
            checkpoint: Checkpoint name
            status: Status (passed, failed, running)
            data: Additional data to send
        """
        if self.qa_callback:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.qa_callback(checkpoint, status, data))
            except Exception:
                pass  # Silently fail if callback fails
