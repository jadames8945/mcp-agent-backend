import logging

from worker.config import worker_app

logger = logging.getLogger(__name__)


@worker_app.task(name="invoke_unified_stream")
def invoke_streamed_response(
        agent_name: str,
        session_id: str,
        user_input: str,
        result_channel: str,
        tool_summaries_str: str,
        chat_history_str: str,
        final_result: str | None = None
) -> bool:
    try:
        from app.agents.streaming_agent.streaming_agent import streaming_handler

        return streaming_handler(
            agent_name=agent_name,
            session_id=session_id,
            user_input=user_input,
            result_channel=result_channel,
            tool_summaries_str=tool_summaries_str,
            chat_history_str=chat_history_str,
            final_result=final_result
        )

    except Exception as e:
        logger.exception(f"Unified streaming task failed: {e}")
        return False


@worker_app.task(name="send_progress_update")
def send_progress_update(
        session_id: str,
        result_channel: str,
        tool_name: str,
        progress_step: int,
        tool_len: int,
        message: str
) -> bool:
    try:
        from app.agents.streaming_agent.streaming_agent import _publish_chunk
        
        progress_message = f"Step {progress_step} of {tool_len}: {tool_name}\n{message}"
        
        logger.info(f"📤 Sending progress update: {progress_message}")
        
        success = _publish_chunk(
            chunk=progress_message,
            channel=result_channel,
            agent_name="workflow_progress",
            progress="progress_update",
            session_id=session_id
        )
        
        if success:
            logger.info(f"✅ Progress update sent successfully to channel {result_channel}")
        else:
            logger.error(f"❌ Failed to send progress update to channel {result_channel}")
        
        return success
        
    except Exception as e:
        logger.exception(f"Progress update task failed: {e}")
        return False
