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
