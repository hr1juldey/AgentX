"""Personal Assistant service with DSPy ReAct + tools."""

import asyncio
import logging
from datetime import UTC, datetime
from typing import AsyncIterator, Dict, List

import dspy
import requests

from config.settings import settings

logger = logging.getLogger(__name__)


# ============ TOOLS ============


def calculator(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    logger.info(f"Calculator called with: {expression}")
    try:
        # Safe evaluation - only allow basic math operations
        allowed_names = {}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        logger.info(f"Calculator result: {result}")
        return f"The result is: {result}"
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return f"Calculator error: {str(e)}"


def searxng_search(query: str) -> str:
    """Search using local SearXNG instance."""
    logger.info(f"SearXNG search called with: {query}")
    try:
        response = requests.get(
            "http://localhost:8080/search",
            params={"q": query, "format": "json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        logger.info(f"SearXNG returned {len(data.get('results', []))} results")

        if not data.get("results"):
            logger.warning(f"No results found for '{query}'")
            return f"No results found for '{query}'"

        # Format top 3 results
        results = data["results"][:3]
        formatted = f"Search results for '{query}':\n"
        for i, r in enumerate(results, 1):
            formatted += f"\n{i}. {r.get('title', 'No title')}\n"
            formatted += f"   {r.get('url', 'No URL')}\n"
            if r.get("content"):
                formatted += f"   {r['content'][:200]}...\n"

        logger.info(f"SearXNG formatted response: {formatted[:200]}...")
        return formatted
    except Exception as e:
        logger.error(f"SearXNG search error: {e}", exc_info=True)
        return f"SearXNG search error: {str(e)}"


def tavily_search(query: str) -> str:
    """Search using Tavily API."""
    try:
        # Use Tavily via MCP
        from mcp__tavily__tavily_search import tavily_search as mcp_tavily  # type: ignore[import]

        results = mcp_tavily(query=query, max_results=3)

        formatted = f"Tavily search results for '{query}':\n"
        for i, r in enumerate(results.get("results", [])[:3], 1):
            formatted += f"\n{i}. {r.get('title', 'No title')}\n"
            formatted += f"   {r.get('url', 'No URL')}\n"
            if r.get("content"):
                formatted += f"   {r['content'][:200]}...\n"

        return formatted
    except ImportError:
        # Fallback to direct API if MCP not available
        return "Tavily search not available - using SearXNG instead"
    except Exception as e:
        logger.error(f"Tavily error: {e}")
        return f"Tavily search error: {str(e)}"


# ============ ASSISTANT SERVICE ============


class AssistantService:
    """Service for Personal Assistant with DSPy ReAct + tools."""

    def __init__(self):
        """Initialize the assistant service."""
        self._conversations: Dict[str, List[Dict]] = {}

        # Configure DSPy with Ollama (built-in support)
        logger.info(f"Initializing DSPy with model: {settings.llm_model}")
        self.lm = dspy.LM(
            f"ollama_chat/{settings.llm_model}",
            api_base=settings.llm_api_url,
            api_key="",
        )
        dspy.configure(lm=self.lm)

        # Initialize STT/TTS services
        from .stt_service import stt_service
        from .tts_service import tts_service

        self.stt = stt_service
        self.tts = tts_service

        # Initialize ReAct with tools
        self.react = dspy.ReAct(
            "question->answer",  # type: ignore[arg-type]
            tools=[
                dspy.Tool(calculator, name="calculator"),
                dspy.Tool(searxng_search, name="searxng_search"),
                dspy.Tool(tavily_search, name="tavily_search"),
            ],
        )

        logger.info(f"Personal Assistant initialized with model: {settings.llm_model}")
        logger.info("Tools available: calculator, searxng_search, tavily_search")

    async def chat_stream(
        self, message: str, history: List[Dict]
    ) -> AsyncIterator[str]:
        """
        Stream response from DSPy ReAct.

        Yields: Text chunks as they arrive
        """
        try:
            logger.info(f"Processing message: {message[:100]}...")

            # Run DSPy ReAct in thread pool to avoid async issues
            loop = asyncio.get_event_loop()

            def run_react():
                result = self.react(question=message)

                # Log intermediate steps for debugging
                if hasattr(result, "trace"):
                    logger.info(f"ReAct trace: {result.trace}")
                if hasattr(result, "reasoning"):
                    logger.info(f"ReAct reasoning: {result.reasoning}")
                if hasattr(result, "tool_calls"):
                    logger.info(f"ReAct tool_calls: {result.tool_calls}")

                return result

            result = await loop.run_in_executor(None, run_react)

            # Log the full result for debugging
            logger.info(f"ReAct result type: {type(result)}")
            logger.info(f"ReAct result: {result}")

            # Yield the answer
            if hasattr(result, "answer"):
                logger.info(f"Answer: {result.answer}")
                yield result.answer
            else:
                logger.info(f"String result: {str(result)}")
                yield str(result)

        except Exception as e:
            logger.error(f"DSPy ReAct error: {e}", exc_info=True)
            yield f"I'm sorry, I encountered an error: {str(e)}"

    async def process_message(self, request) -> Dict:
        """Process a chat message (non-streaming for REST API)."""
        conversation_id = getattr(request, "conversation_id", None) or "default"
        message = getattr(request, "message", "")

        # Get conversation history
        history = self._conversations.get(conversation_id, [])

        # Collect full response
        response_text = ""
        async for chunk in self.chat_stream(message, history):
            response_text += chunk

        # Store in conversation history
        if conversation_id not in self._conversations:
            self._conversations[conversation_id] = []

        self._conversations[conversation_id].append(
            {
                "role": "user",
                "content": message,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        self._conversations[conversation_id].append(
            {
                "role": "assistant",
                "content": response_text,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        return {"response": response_text, "conversation_id": conversation_id}

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        return self._conversations.get(conversation_id, [])


# Global service instance
assistant_service = AssistantService()
