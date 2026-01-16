"""Personal Assistant service with DSPy ReAct pattern."""
import logging
from typing import Dict, List, Optional
from datetime import datetime, UTC

from config.settings import settings
from models.schemas import ChatRequest

logger = logging.getLogger(__name__)


class CalculatorTool:
    """Simple calculator tool."""
    
    def execute(self, expression: str) -> str:
        """Evaluate a mathematical expression."""
        try:
            # Safe evaluation of basic math
            result = eval(expression, {"__builtins__": {}}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Error: {str(e)}"


class SearchTool:
    """Mock search tool."""
    
    def execute(self, query: str) -> str:
        """Mock search implementation."""
        return f"Search results for: {query}\n- Result 1: Mock data\n- Result 2: Mock data"


class WeatherTool:
    """Mock weather tool."""
    
    def execute(self, location: str) -> str:
        """Mock weather implementation."""
        return f"Weather in {location}: 22°C, Partly cloudy"


class AssistantService:
    """Service for Personal Assistant with ReAct pattern."""
    
    def __init__(self):
        """Initialize the assistant service."""
        self.tools = {
            "calculator": CalculatorTool(),
            "search": SearchTool(),
            "weather": WeatherTool()
        }
        self._conversations: Dict[str, List[Dict]] = {}
        logger.info("Personal Assistant service initialized")
    
    async def process_message(self, request: ChatRequest) -> Dict:
        """Process a chat message with ReAct pattern."""
        conversation_id = request.conversation_id or "default"
        message = request.message
        
        # Simple ReAct simulation
        response_text = await self._generate_response(message)
        
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
            "thoughts": f"Processing: {message}",
            "conversation_id": conversation_id
        }
    
    async def _generate_response(self, message: str) -> str:
        """Generate a response (simplified ReAct)."""
        message_lower = message.lower()
        
        # Check for calculator
        if any(word in message_lower for word in ["calculate", "math", "compute", "+", "-", "*", "/"]):
            try:
                # Extract expression
                expr = message.split("calculate")[-1].strip()
                if not expr:
                    expr = message
                return self.tools["calculator"].execute(expr)
            except:
                return "I can help with calculations. What would you like me to calculate?"
        
        # Check for search
        if any(word in message_lower for word in ["search", "find", "look up"]):
            query = message.split("search")[-1].strip()
            return self.tools["search"].execute(query)
        
        # Check for weather
        if "weather" in message_lower:
            location = message.split("weather")[-1].strip() or "your location"
            return self.tools["weather"].execute(location)
        
        # Default response
        return "I'm a personal assistant. I can help with calculations, searches, and weather queries. Try asking me to calculate something or search for information."
    
    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """Get conversation history."""
        return self._conversations.get(conversation_id, [])


# Global service instance
assistant_service = AssistantService()
