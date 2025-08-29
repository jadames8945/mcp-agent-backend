import logging
from typing import List, Dict

from fastapi import APIRouter, HTTPException, Depends
from starlette.websockets import WebSocket

from app.managers.ConnectionManager import ConnectionManager
from app.models.mcp_config import MultiMCPConfig
from app.schemas.tool_summaries import ToolSummary
from app.schemas.tool_summary_request import ToolSummaryRequest
from app.services.agent_invocation_service import AgentInvocationService
from app.services.tool_summaries_service import ToolSummariesService

router = APIRouter(
    prefix="/tool-summary",
    tags=["tool-summary"],
)

logger = logging.getLogger("tool-summary")


def get_tool_summaries_service():
    return ToolSummariesService()


def get_connection_manager():
    return ConnectionManager()


def get_agent_invocation_service():
    return AgentInvocationService()


@router.get("/test")
async def test_endpoint():
    return {"status": "ok", "message": "Backend is working!"}

@router.post(path="", response_model=Dict[str, List[ToolSummary]])
async def get_tools(
        request: ToolSummaryRequest,
        tool_summaries_service: ToolSummariesService = Depends(get_tool_summaries_service),
) -> Dict[str, List[ToolSummary]]:
    try:
        result = await tool_summaries_service.fetch_tool_summaries(
            session_id=request.session_id,
            mcp_config=request.mcp_config
        )
        return result.servers
    except Exception as e:
        logger.exception("Failed to fetch tool summaries")
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        session_id: str,
        manager: ConnectionManager = Depends(get_connection_manager),
        agent_invocation_service: AgentInvocationService = Depends(get_agent_invocation_service)
) -> None:
    try:
        await manager.connect(websocket, session_id)
        logger.info(f"WebSocket connected for session: {session_id}")
        
        # Send a connection confirmation
        await websocket.send_json({"type": "connection_established", "session_id": session_id})
        
        while True:
            try:
                # Wait for messages with a timeout to prevent hanging
                websocket_data = await websocket.receive_json()
                if not websocket_data:
                    logger.info(f"Empty message received for session {session_id}, continuing...")
                    continue
                    
                logger.info(f"Processing message for session {session_id}: {websocket_data.get('user_input', 'No user input')}")
                from app.util.websocket_helpers import handle_websocket_message
                await handle_websocket_message(websocket, session_id, websocket_data, agent_invocation_service)
                logger.info(f"Message processing completed for session {session_id}")
                
            except Exception as message_error:
                logger.exception(f"Error processing message for session {session_id}")
                try:
                    await websocket.send_json({"error": f"Message processing failed: {str(message_error)}"})
                except Exception:
                    # If we can't send the error, the connection is probably broken
                    break
                continue
                
    except Exception as e:
        logger.exception(f"WebSocket error for session {session_id}")
    finally:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session: {session_id}")
