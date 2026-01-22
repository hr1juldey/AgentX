# =============================================================================
# AGENTX PRESENTER - Progress Tracker
# =============================================================================
# Progress tracking for presenter pipeline phases
# =============================================================================


class PresenterProgressTracker:
    """Tracks progress of presenter pipeline phases."""

    _progress_map = {
        "checking": 33.0,
        "polishing": 66.0,
        "finalizing": 100.0,
    }

    @classmethod
    def get_progress_status(cls, phase: str = "polishing") -> dict:
        """Get progress status for UI updates.

        Args:
            phase: Current phase (checking, polishing, finalizing)

        Returns:
            Progress status dict with phase, status, message, completion_percentage
        """
        return {
            "phase": phase,
            "status": "running",
            "message": f"Presenter: {phase.capitalize()} widgets...",
            "completion_percentage": cls.get_phase_progress(phase),
        }

    @classmethod
    def get_phase_progress(cls, phase: str) -> float:
        """Get completion percentage for phase.

        Args:
            phase: Phase name

        Returns:
            Completion percentage (0-100)
        """
        return cls._progress_map.get(phase.lower(), 50.0)
