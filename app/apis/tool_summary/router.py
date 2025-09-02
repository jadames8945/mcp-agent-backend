import json
import logging
from typing import List, Dict, AsyncGenerator
import uuid
from fastapi import APIRouter, HTTPException, Depends, WebSocketDisconnect
from starlette.websockets import WebSocket
from app.managers.ConnectionManager import ConnectionManager
from app.models.mcp_config import MultiMCPConfig
from app.schemas.tool_summaries import ToolSummary
from app.schemas.tool_summary_request import ToolSummaryRequest
from app.services.agent_invocation_service import AgentInvocationService
from app.services.tool_summaries_service import ToolSummariesService
from app.util.websocket_helpers import handle_websocket_message
from common.services.redis_service import get_redis_client
from redis.asyncio import Redis
router = APIRouter(
    prefix="/tool-summary",
    tags=["tool-summary"],
)
async def get_redis_client_dependency() -> AsyncGenerator[Redis, None]:
    """Get async Redis client - creates new connection for each request."""
    async for client in get_redis_client():
        yield client
logger = logging.getLogger("tool-summary")
async def handle_ack(data, redis):
    """Handle acknowledgment messages from websocket."""
    stream_id = data.get("stream_id")
    result_channel = data.get("result_channel")
    if stream_id and result_channel:
        try:
            await redis.xack(result_channel, "websocket-consumer-group", stream_id)
            logger.info(f"ACKed message {stream_id} on {result_channel}")
        except Exception as e:
            logger.warning(f"Failed to ACK message: {e}")
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
@router.websocket("/ws")
async def websocket_endpoint(
        websocket: WebSocket,
        redis: Redis = Depends(get_redis_client_dependency)
) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())
    redis_tasks = set()
    await websocket.send_json({
        "type": "session_established",
        "session_id": session_id
    })
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            if data.get("type") == "ack":
                await handle_ack(data, redis)
                continue
            await handle_websocket_message(
                websocket=websocket,
                websocket_data=data,
                session_id=session_id,
                agent_invocation_service=get_agent_invocation_service()
            )
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: session_id={session_id}")
        for task in redis_tasks:
            task.cancel()
