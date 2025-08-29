import json
import logging

from langchain.agents import AgentExecutor, create_react_agent, create_tool_calling_agent
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agents.chat_agent.chat_agent import ChatAgent
from app.agents.summary_agent.summary_agent import SummaryAgent
from app.caches.conversation_store import ConversationSession, ConversationStore
from app.infrastructure import infra

logger = logging.getLogger(__name__)


def get_agent_instance_prompt(agent_name: str) -> ChatPromptTemplate:
    if agent_name == "chat_agent":
        return ChatAgent().prompt()

    return SummaryAgent().prompt()


def build_formatted_prompt(
        agent_name: str,
        agent_prompt: ChatPromptTemplate,
        user_input: str,
        chat_history_str: str,
        tool_summaries_str: str,
        final_result: str | None = None
) -> PromptValue:
    if agent_name == "summary_agent" and final_result is None:
        raise Exception("final_result cannot be None")

    if isinstance(chat_history_str, list):
        chat_history = chat_history_str
    else:
        chat_history = [{"role": "user", "content": chat_history_str}]

    if agent_name == "summary_agent":
        return agent_prompt.format_prompt(chat_history=chat_history, final_result=final_result)

    return agent_prompt.format_prompt(chat_history=chat_history, available_tools=tool_summaries_str, user_input=user_input)


def build_streaming_agent(
        agent_prompt: ChatPromptTemplate,
) -> AgentExecutor:
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        streaming=True
    )
    agent = create_tool_calling_agent(
        llm=llm,
        tools=[],
        prompt=agent_prompt
    )

    return AgentExecutor(
        agent=agent,
        tools=[],
        verbose=True
    )


def _publish_chunk(
        chunk: str,
        channel: str,
        agent_name: str,
        progress: str,
        session_id: str = None,
        final_result: dict = None
) -> bool:
    try:
        redis_client = infra.redis_client

        message = {
            "agent_name": str(agent_name),
            "progress": progress,
            "chunk": chunk,
            "session_id": session_id
        }

        if final_result:
            message["result"] = json.dumps(final_result)

        redis_client.xadd(channel, message, maxlen=1000, approximate=True)
        return True
    except Exception as e:
        logger.exception(f"Failed to publish chunk: {e}")
        return False


def _publish_streaming_chunks(
        agent_executor,
        result_channel: str,
        agent_name: str,
        session_id: str,
        formatted_prompt: PromptValue,
        user_input: str,
        chat_history_str: str,
        tool_summaries_str: str,
        final_result: str = None
) -> str:
    full_response = ""
    
    if agent_name == "summary_agent":
        inputs = {
            "chat_history": chat_history_str if isinstance(chat_history_str, str) else str(chat_history_str),
            "final_result": final_result or "",
            "agent_scratchpad": ""
        }
    else:
        inputs = {
            "chat_history": chat_history_str if isinstance(chat_history_str, list) else [{"role": "user", "content": chat_history_str}],
            "available_tools": tool_summaries_str,
            "user_input": user_input,
            "agent_scratchpad": ""
        }
    
    for chunk in agent_executor.stream(inputs):
        if hasattr(chunk, 'content') and chunk.content:
            chunk_content = chunk.content
        elif isinstance(chunk, dict) and 'output' in chunk:
            chunk_content = chunk['output']
        elif isinstance(chunk, str):
            chunk_content = chunk
        else:
            chunk_content = str(chunk)

        if chunk_content and chunk_content.strip():
            full_response += chunk_content

            _publish_chunk(
                chunk=chunk_content,
                channel=result_channel,
                agent_name=agent_name,
                progress="streaming",
                session_id=session_id
            )

    return full_response


def _publish_final_response(
        full_response: str,
        user_input: str,
        result_channel: str,
        agent_name: str,
        session_id: str,
):
    conversation_session: ConversationSession = ConversationStore().get_session(session_id=session_id)

    conversation_session.add_message({
        "role": "user",
        "content": user_input
    })

    conversation_session.add_message({
        "role": "assistant",
        "content": full_response
    })

    _publish_chunk(
        chunk="",
        channel=result_channel,
        agent_name=agent_name,
        progress="complete",
        session_id=session_id,
        final_result={"response": full_response}
    )

    logger.info(f"Streaming completed for {agent_name} in session: {session_id}")


def streaming_handler(
        agent_name: str,
        session_id: str,
        user_input: str,
        result_channel: str,
        tool_summaries_str: str,
        chat_history_str: str,
        final_result: str | None = None
) -> bool:
    try:
        agent_prompt: ChatPromptTemplate = get_agent_instance_prompt(agent_name=agent_name)

        formatted_prompt: PromptValue = build_formatted_prompt(
            agent_name=agent_name,
            agent_prompt=agent_prompt,
            user_input=user_input,
            chat_history_str=chat_history_str,
            tool_summaries_str=tool_summaries_str,
            final_result=final_result
        )

        agent_executor = build_streaming_agent(agent_prompt=agent_prompt)

        _publish_chunk(
            chunk="",
            channel=result_channel,
            agent_name=agent_name,
            progress="started",
            session_id=session_id
        )

        full_response: str = _publish_streaming_chunks(
            agent_executor=agent_executor,
            result_channel=result_channel,
            agent_name=agent_name,
            session_id=session_id,
            formatted_prompt=formatted_prompt,
            user_input=user_input,
            chat_history_str=chat_history_str,
            tool_summaries_str=tool_summaries_str,
            final_result=final_result
        )

        if full_response:
            _publish_final_response(
                full_response,
                user_input,
                result_channel,
                agent_name,
                session_id
            )
            return True

        return True

    except Exception as e:
        logger.exception(f"Streaming failed for {agent_name}: {e}")

        _publish_chunk(
            chunk="",
            channel=result_channel,
            agent_name=agent_name,
            progress="error",
            session_id=session_id,
            final_result={"error": str(e)}
        )

        return False
