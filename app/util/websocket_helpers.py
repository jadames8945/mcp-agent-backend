import logging
import asyncio
from typing import Dict, Any
from starlette.websockets import WebSocket

from app.models.mcp_config import MultiMCPConfig
from app.services.agent_invocation_service import AgentInvocationService
from common.services.redis_service import get_redis_client, listen_and_forward_redis_stream

logger = logging.getLogger(__name__)

async def handle_websocket_message(
    websocket: WebSocket,
    session_id: str,
    websocket_data: Dict[str, Any],
    agent_invocation_service: AgentInvocationService
) -> None:
    logger.info(f"Starting to handle WebSocket message for session {session_id}")
    
    try:
        user_input = websocket_data.get("user_input")
        if not user_input:
            await websocket.send_json({"error": "User input is missing"})
            return

        mcp_config_data = websocket_data.get("mcp_config")
        if not mcp_config_data:
            await websocket.send_json({"error": "Invalid MCP configuration"})
            return

        try:
            mcp_config = MultiMCPConfig(**mcp_config_data)
        except Exception as e:
            await websocket.send_json({"error": f"Invalid MCP config format: {str(e)}"})
            return

        try:
            redis_client = await anext(get_redis_client())
            logger.info(f"Got Redis client for session {session_id}")
            
            # Get the actual result_channel from agent invocation
            logger.info(f"Calling agent invocation for session {session_id}")
            invocation_result = await agent_invocation_service.handle_agent_invocation(
                user_input=user_input,
                mcp_config=mcp_config,
                session_id=session_id,
            )
            
            if not invocation_result or "result_channel" not in invocation_result:
                logger.error(f"Failed to get result channel for session {session_id}: {invocation_result}")
                await websocket.send_json({"error": "Failed to get result channel from agent invocation"})
                return
                
            result_channel = invocation_result["result_channel"]
            logger.info(f"Got result channel {result_channel} for session {session_id}")
            
            await websocket.send_json({
                "status": "processing", 
                "result_channel": result_channel
            })
            
            # Start Redis stream task - it will forward messages as they come
            logger.info(f"Starting Redis stream task for session {session_id}")
            asyncio.create_task(
                listen_and_forward_redis_stream(
                    redis=redis_client,
                    result_channel=result_channel,
                    websocket=websocket
                )
            )
            
            logger.info(f"Redis stream task started for session {session_id}")
            
        except Exception as e:
            await websocket.send_json({"error": f"Agent invocation failed: {str(e)}"})
            logger.exception(f"Agent invocation error for session {session_id}")
            raise
    except Exception as e:
        logger.exception(f"WebSocket message handling error for session {session_id}")
        await websocket.send_json({"error": f"WebSocket error: {str(e)}"}) 