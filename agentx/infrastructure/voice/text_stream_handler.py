"""Text Stream Handler - STT buffering and TTS sentence splitting."""

from collections.abc import Callable


class TextStreamHandler:
    """Handle STT text buffering and TTS sentence splitting."""

    def __init__(self) -> None:
        """Initialize the text stream handler.

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError("TextStreamHandler not yet implemented")

    def buffer_stt_chunk(self, session_id: str, text: str) -> None:
        """Buffer STT text chunk until Eos.

        Args:
            session_id: Session identifier
            text: Text chunk to buffer

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "TextStreamHandler.buffer_stt_chunk() not yet implemented"
        )

    def get_stt_text(self, session_id: str) -> str:
        """Get complete STT text after Eos.

        Args:
            session_id: Session identifier

        Returns:
            Complete text

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "TextStreamHandler.get_stt_text() not yet implemented"
        )

    async def stream_tts_sentences(
        self, session_id: str, text: str, on_sentence: Callable
    ) -> None:
        """Split TTS text into sentences and stream.

        Args:
            session_id: Session identifier
            text: Text to split and stream
            on_sentence: Callback for each sentence

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "TextStreamHandler.stream_tts_sentences() not yet implemented"
        )

    def interrupt_tts(self, session_id: str) -> None:
        """Interrupt ongoing TTS for session.

        Args:
            session_id: Session identifier

        Raises:
            NotImplementedError: If not yet implemented
        """
        raise NotImplementedError(
            "TextStreamHandler.interrupt_tts() not yet implemented"
        )
