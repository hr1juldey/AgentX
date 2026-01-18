# =============================================================================
# AGENTX R013 - Logging Configuration
# =============================================================================
# Centralized logging setup for file and console output
# =============================================================================

import io
import logging
import sys
from pathlib import Path


def setup_logging() -> logging.FileHandler:
    """Configure logging to file and console.

    Returns:
        File handler for stderr capture.
    """
    # Configure logging to file
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "server.log"

    # Capture warnings into logging
    logging.captureWarnings(True)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    )

    # File handler - captures everything including warnings
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Configure root logger to capture all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Also set up warnings logger to capture warning messages
    warnings_logger = logging.getLogger("py.warnings")
    warnings_logger.setLevel(logging.WARNING)
    warnings_logger.addHandler(file_handler)
    warnings_logger.addHandler(console_handler)

    # Filter DSPy/Ollama Pydantic warnings (cosmetic, from OpenAI-compatibility mode)
    # These appear because Ollama's response format differs from OpenAI's schema
    class PydanticWarningFilter(logging.Filter):
        """Filter out Pydantic serialization warnings from DSPy/Ollama."""

        def filter(self, record: logging.LogRecord) -> bool:
            return (
                "PydanticSerializationUnexpectedValue" not in record.getMessage()
                and "Expected `Message`" not in record.getMessage()
                and "Expected `StreamingChoices`" not in record.getMessage()
            )

    pydantic_filter = PydanticWarningFilter()
    warnings_logger.addFilter(pydantic_filter)

    return file_handler


class StderrCapture(io.TextIOWrapper):
    """Capture stderr and write to both file and original stderr.

    Inherits from io.TextIOWrapper to be compatible with sys.stderr type.
    """

    def __init__(self, file_handler: logging.FileHandler) -> None:
        # Store the original stderr
        self._original_stderr = sys.stderr
        # Initialize TextIOWrapper with a dummy buffer
        super().__init__(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
        self.file_handler = file_handler

    def write(self, message: str) -> int:
        """Write message to both log file and original stderr.

        Returns:
            Number of characters written.
        """
        # Write to log file
        if message.strip():
            self.file_handler.stream.write(message)
            self.file_handler.stream.flush()
        # Also write to original stderr
        return self._original_stderr.write(message)

    def flush(self) -> None:
        """Flush both streams."""
        self.file_handler.stream.flush()
        self._original_stderr.flush()
