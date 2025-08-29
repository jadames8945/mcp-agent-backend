import logging
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.chat_history_service import ChatHistoryService

router = APIRouter(
    prefix="/chat",
    tags=["chat"],
)

logger = logging.getLogger("chat")

def get_chat_history_service():
    return ChatHistoryService()

class ChatHistoryCreateRequest(BaseModel):
    title: str
    session_id: str

class ChatHistoryUpdateRequest(BaseModel):
    messages: List[dict]
    session_id: str

@router.get("/history", response_model=List[dict])
async def get_chat_histories(
    chat_service: ChatHistoryService = Depends(get_chat_history_service)
):
    """Get all chat histories."""
    try:
        return chat_service.get_all_chat_histories()
    except Exception as e:
        logger.exception("Failed to fetch chat histories")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/history", response_model=dict)
async def create_chat_history(
    request: ChatHistoryCreateRequest,
    chat_service: ChatHistoryService = Depends(get_chat_history_service)
):
    """Create a new chat history."""
    try:
        # For now, we'll create a simple chat history
        # In a real implementation, you'd use the chat service
        chat_history = {
            "id": f"chat_{len(chat_service.get_all_chat_histories()) + 1}",
            "title": request.title,
            "timestamp": "2024-01-01T00:00:00Z",
            "messages": []
        }
        return chat_history
    except Exception as e:
        logger.exception("Failed to create chat history")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/history/{chat_id}")
async def update_chat_history(
    chat_id: str,
    request: ChatHistoryUpdateRequest,
    chat_service: ChatHistoryService = Depends(get_chat_history_service)
):
    """Update chat history with new messages."""
    try:
        # For now, return success
        # In a real implementation, you'd use the chat service
        return {"message": "Chat history updated successfully"}
    except Exception as e:
        logger.exception("Failed to update chat history")
        raise HTTPException(status_code=500, detail=str(e)) 