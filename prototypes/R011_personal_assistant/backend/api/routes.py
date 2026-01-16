"""API routes."""
from fastapi import APIRouter, HTTPException
from models.schemas import ChatRequest, ChatResponse, ToolSchema
from services.service import assistant_service

router = APIRouter(tags=["assistant"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message with the ReAct agent."""
    try:
        response = await assistant_service.process_message(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools", response_model=list[ToolSchema])
async def list_tools():
    """List available tools."""
    from services.service import assistant_service
    tools = []
    for name, tool in assistant_service.tools.items():
        tools.append(ToolSchema(name=name, description=tool.description, parameters={}))
    return tools


@router.get("/health")
async def health():
    return {"status": "healthy", "agent_ready": True}
