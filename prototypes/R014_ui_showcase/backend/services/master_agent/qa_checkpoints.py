# =============================================================================
# AGENTX QA Checkpoints Module
# =============================================================================
# Quality assurance checkpoint system for Master Agent
# =============================================================================

from typing import Callable, Optional
from dataclasses import dataclass, field


@dataclass
class QACheckpoint:
    """Represents a single QA checkpoint."""

    name: str
    description: str
    passed: bool = False
    checklist: dict = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class QAReport:
    """Complete QA report for the pipeline."""

    checkpoints: list[QACheckpoint] = field(default_factory=list)
    final_status: str = "pending"  # pending, passed, failed
    errors: list[str] = field(default_factory=list)

    def add_checkpoint(self, checkpoint: QACheckpoint) -> None:
        """Add a checkpoint to the report."""
        self.checkpoints.append(checkpoint)

    def mark_passed(self, checkpoint_name: str, checklist: dict) -> None:
        """Mark a checkpoint as passed."""
        for cp in self.checkpoints:
            if cp.name == checkpoint_name:
                cp.passed = True
                cp.checklist = checklist
                break

    def mark_failed(self, checkpoint_name: str, error: str) -> None:
        """Mark a checkpoint as failed."""
        for cp in self.checkpoints:
            if cp.name == checkpoint_name:
                cp.passed = False
                cp.error_message = error
                break
        self.errors.append(f"{checkpoint_name}: {error}")

    def finalize(self) -> None:
        """Finalize the QA report."""
        failed = any(not cp.passed for cp in self.checkpoints)
        self.final_status = "failed" if failed else "passed"


class QACheckpointModule:
    """DSPy module for managing QA checkpoints."""

    # Standard checkpoint definitions
    CHECKPOINTS = [
        "analysis_qa",
        "research_qa",
        "contextualization_qa",
        "judgment_qa",
        "design_qa",
        "widget_selection_qa",
        "sequence_qa",
        "presentation_qa",
        "hydration_qa",
    ]

    def __init__(self):
        self.report = QAReport()
        for checkpoint_name in self.CHECKPOINTS:
            self.report.add_checkpoint(
                QACheckpoint(
                    name=checkpoint_name,
                    description=f"QA checkpoint for {checkpoint_name}",
                )
            )

    def mark_failed(self, checkpoint_name: str, error: str) -> None:
        """Mark a checkpoint as failed (convenience method)."""
        self.report.mark_failed(checkpoint_name, error)

    def validate_checkpoint(
        self,
        checkpoint_name: str,
        data: dict,
        validator_func: Optional[Callable] = None,
    ) -> bool:
        """Validate a checkpoint with optional custom validator."""
        if checkpoint_name not in self.CHECKPOINTS:
            self.report.mark_failed(checkpoint_name, "Unknown checkpoint")
            return False

        try:
            if validator_func:
                result = validator_func(data)
                if result:
                    self.report.mark_passed(checkpoint_name, data)
                    return True
                else:
                    self.report.mark_failed(checkpoint_name, "Validation failed")
                    return False
            else:
                # Default validation: check that data is not empty
                if data and not all(v is None for v in data.values()):
                    self.report.mark_passed(checkpoint_name, data)
                    return True
                else:
                    self.report.mark_failed(checkpoint_name, "Empty data")
                    return False
        except Exception as e:
            self.report.mark_failed(checkpoint_name, str(e))
            return False

    def get_checklist_for_ui(self) -> dict:
        """Get checklist formatted for UI display."""
        return {
            "checkpoints": [
                {
                    "name": cp.name,
                    "description": cp.description,
                    "status": "passed" if cp.passed else "pending",
                    "checklist": cp.checklist,
                    "error": cp.error_message,
                }
                for cp in self.report.checkpoints
            ],
            "final_status": self.report.final_status,
            "errors": self.report.errors,
        }

    def finalize_report(self) -> QAReport:
        """Finalize and return the complete QA report."""
        self.report.finalize()
        return self.report
