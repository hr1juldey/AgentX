"""Personal Assistant service with DSPy ReAct + streaming."""
import logging
from datetime import UTC, datetime
from typing import AsyncIterator, Dict, List

import dspy
import dspy.streaming

from config.settings import settings

logger = logging.getLogger(__name__)


# Simple tools for DSPy
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


def search(query: str) -> str:
    """Mock search implementation."""
    return f"Search results for: {query}\n- Result 1: Mock data\n- Result 2: Mock data"


def weather(location: str) -> str:
    """Mock weather implementation."""
    return f"Weather in {location}: 22°C, Partly cloudy"


class AssistantService:
    """Service for Personal Assistant with DSPy ReAct + streaming."""

    def __init__(self):
        """Initialize the assistant service."""
        self._conversations: Dict[str, List[Dict]] = {}

        # Configure DSPy with Ollama (built-in support)
        logger.info(f"Initializing DSPy with model: {settings.llm_model}")
        self.lm = dspy.LM(
            f"ollama_chat/{settings.llm_model}",
            api_base=settings.llm_api_url,
            api_key=""
        )
        dspy.configure(lm=self.lm)

        # Initialize STT/TTS services
        from .stt_service import stt_service
        from .tts_service import tts_service
        self.stt = stt_service
        self.tts = tts_service

        # Initialize ReAct with streaming
        self.react = dspy.ReAct("question->answer", tools=[
            dspy.Tool(calculator, name="calculator"),
            dspy.Tool(search, name="search"),
            dspy.Tool(weather, name="weather"),
        ])

        # Wrap with streaming
        stream_listeners = [
            dspy.streaming.StreamListener(
                signature_field_name="next_thought",
                allow_reuse=True
            )
        ]
        self.stream_react = dspy.streamify(
            self.react,
            stream_listeners=stream_listeners
        )

        logger.info(f"Personal Assistant initialized with model: {settings.llm_model}")

    async def chat_stream(self, message: str, history: List[Dict]) -> AsyncIterator[str]:
        """
        Stream response from DSPy ReAct.

        Yields: Text chunks as they arrive
        """
        try:
            output_stream = self.stream_react(question=message)

            for chunk in output_stream:
                if isinstance(chunk, dspy.streaming.StreamResponse):
                    yield chunk.chunk
                elif isinstance(chunk, dspy.Prediction):
                    if hasattr(chunk, 'answer'):
                        yield chunk.answer
                    break

        except Exception as e:
            logger.error(f"DSPy streaming error: {e}")
            yield "I'm sorry, I encountered an error."

    async def process_message(self, request) -> Dict:
        """Process a chat message (non-streaming for REST API)."""
        conversation_id = getattr(request, 'conversation_id', None) or "default"
        message = getattr(request, 'message', '')

        # Collect full response
        response_text = ""
        async for chunk in self.chat_stream(message, []):
            response_text += chunk

        # Store in conversation history
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now(UTC).isoformat()
        })

        self._conversations[conversation_id].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.now(UTC).isoformat()
        })

        return {
            "response": response_text,
            "conversation_id": conversation_id
        }

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        return self._conversations.get(conversation_id, [])


# Global service instance
assistant_service = AssistantService()
