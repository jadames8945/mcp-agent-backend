import json
import logging
import uuid

from app.agents.chat_agent.chat_agent import ChatAgent
from app.agents.router_agent.router_agent import RouterAgent
from app.caches.conversation_store import ConversationSession
from app.infrastructure import infra
from app.models.mcp_config import MultiMCPConfig
from app.schemas.router_decision import RouterDecision
from app.schemas.tool_summaries import ToolsSummaryByServer
from app.services.tool_summaries_service import ToolSummariesService
from common.utils.tool_util import format_tool_by_server_name

logger = logging.getLogger(__name__)
class AgentInvocationService:
    def __init__(self):
        self.conversation_store = infra.conversation_store
        self.tool_summaries_service = ToolSummariesService()

    def handle_router_decision(
            self,
            user_input: str,
            tool_summaries_str: str,
            conversation_session: ConversationSession
    ) -> RouterDecision:

        router_agent = RouterAgent()

        return router_agent.handle_router_decision(
            user_input=user_input,
            conversation_session=conversation_session,
            tool_summaries_str=tool_summaries_str
        )

    async def handle_agent_invocation(
            self,
            user_input: str,
            session_id: str,
            mcp_config: MultiMCPConfig
    ) -> dict:
        conversation_session = self.conversation_store.get_session(session_id)
        logger.info(f"Inside handle_agent_invocation session:{session_id}")
        tool_summaries: ToolsSummaryByServer = await self.tool_summaries_service.fetch_missing_tool_summaries(
            session_id=session_id,
            mcp_config=mcp_config
        )

        logger.info(f"Fetched tool summaries:{tool_summaries}")

        tool_summaries_str = format_tool_by_server_name(tool_summaries)

        router_decision = self.handle_router_decision(
            user_input=user_input,
            tool_summaries_str=tool_summaries_str,
            conversation_session=conversation_session
        )

        if router_decision.use_tools:
            mcp_service = await self.tool_summaries_service.get_mcp_service(session_id)

            result = await self._handle_tool_orchestration(
                session_id=session_id,
                user_input=user_input,
                mcp_service=mcp_service,
                tool_summaries_str=tool_summaries_str,
                conversation_session=conversation_session
            )
        else:
            result = await self._handle_chat_response_task(
                session_id=session_id,
                user_input=user_input,
                tool_summaries_str=tool_summaries_str,
                conversation_session=conversation_session
            )
            
        return result

    async def _handle_tool_orchestration(
            self,
            session_id: str,
            user_input: str,
            mcp_service,
            tool_summaries_str: str,
            conversation_session: ConversationSession
    ):
        from app.graph.tool_orchestration_graph import ToolOrchestrationGraph

        result_channel = f"tool_orchestration_{session_id}_{uuid.uuid4().hex}"

        await ToolOrchestrationGraph().run(
            session_id=session_id,
            result_channel=result_channel,
            query=user_input,
            tool_summaries_str=tool_summaries_str,
            mcp_service=mcp_service,
            conversation_session=conversation_session
        )
        return {"status": "processing", "result_channel": result_channel}

    async def _handle_chat_response_task(
            self,
            session_id: str,
            user_input: str,
            tool_summaries_str: str,
            conversation_session: ConversationSession
    ):
        from worker.tasks import invoke_streamed_response
        import uuid

        result_channel = f"chat_response_{session_id}_{uuid.uuid4().hex}"

        invoke_streamed_response.delay(
            agent_name="chat_agent",
            session_id=session_id,
            user_input=user_input,
            tool_summaries_str=tool_summaries_str,
            result_channel=result_channel,
            chat_history_str=conversation_session.get_last_n_messages(10)
        )

        return {"status": "processing", "result_channel": result_channel}
