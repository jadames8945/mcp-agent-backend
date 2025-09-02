import json
import logging
from typing import TypedDict, List, Any, Dict, Optional

from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.tool_orchestration_agent.tool_orchestration_agent import ToolOrchestrationAgent
from app.agents.tool_refinement_agent.tool_refinement_agent import ToolRefinementAgent
from app.caches.conversation_store import ConversationSession
from app.schemas.tool_invocation import ToolInvocations, ToolInvocation
from app.schemas.tool_result import ToolResult
from app.services.mcp_service import MCPService
from app.utils.chat_util import format_final_summary_result

logger = logging.getLogger(__name__)


class MultiAgentStepState(TypedDict):
    session_id: str
    result_channel: str
    query: str
    tool_summaries_str: str
    mcp_service: MCPService
    tool_invocations: ToolInvocations
    conversation_session: ConversationSession


class ToolOrchestrationGraph:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self) -> CompiledStateGraph:
        builder = StateGraph(MultiAgentStepState)
        builder.add_node("tool_orchestrator", self.tool_orchestrator_node)
        builder.add_node("tool_planner", self.planner_node)

        builder.set_entry_point("tool_orchestrator")
        builder.add_edge("tool_orchestrator", "tool_planner")
        builder.set_finish_point("tool_planner")

        return builder.compile()

    async def tool_orchestrator_node(self, state: MultiAgentStepState) -> Optional[MultiAgentStepState]:
        try:
            tool_orchestrator_agent: ToolOrchestrationAgent = ToolOrchestrationAgent()

            response: ToolInvocations = tool_orchestrator_agent.invoke_multi_step_agent(
                tool_summaries_str=state["tool_summaries_str"],
                user_input=state["query"],
                conversation_session=state["conversation_session"]
            )

            if response is None or not response.tools:
                return None

            state["tool_invocations"] = response

            return state
        except Exception as e:
            logger.error(f"Error invoking multi-step agent: {e}")
            return None

    async def planner_node(self, state: Optional[MultiAgentStepState]) -> str | None:
        if state is None:
            return None

        tools = state["tool_invocations"].tools

        if not tools:
            fallback_prompt = self.create_fallback_response(state, error_message="No tool invocations found.")
            
            self._invoke_streamed_response(
                agent_name="chat_agent",
                session_id=state["session_id"],
                user_input=state["query"],
                result_channel=state["result_channel"],
                tool_summaries_str=state["tool_summaries_str"],
                chat_history_str=state["conversation_session"].get_last_n_messages(10)
            )
            return None

        tool_refinement_agent: ToolRefinementAgent = ToolRefinementAgent()
        tool_summaries_str: str = state["tool_summaries_str"]
        mcp_service: MCPService = state["mcp_service"]
        conversation_session: ConversationSession = state["conversation_session"]
        user_input: str = state["query"]
        result_channel: str = state["result_channel"]
        previous_result: List[Dict[str, Any]] = []
        sorted_tools: List[ToolInvocation] = sorted(tools, key=lambda t: t.rank)
        tools_length = len(sorted_tools)

        tool_results: List[ToolResult] = []

        self._send_progress_update(
            session_id=state["session_id"],
            result_channel=result_channel,
            tool_name="workflow_start",
            progress_step=0,
            tool_len=tools_length,
            message=f"Starting workflow with {tools_length} tool invocations..."
        )

        for idx, tool in enumerate(sorted_tools, 1):
            self._send_progress_update(
                session_id=state["session_id"],
                result_channel=result_channel,
                tool_name=tool.tool_name,
                progress_step=idx,
                tool_len=tools_length,
                message=f"Executing {tool.tool_name}..."
            )

            try:
                updated_tool: ToolInvocation = tool_refinement_agent.refine_tool_invocation(
                    user_input=user_input,
                    tool_invocation=tool,
                    previous_result=previous_result,
                    conversation_session=conversation_session,
                    tool_summaries_str=tool_summaries_str
                )

                logger.info(f"ToolRefinementAgent updated tool invocation: {updated_tool}")

                result = await self._invoke_and_store_tool(
                    user_input=user_input,
                    mcp_service=mcp_service,
                    conversation_session=conversation_session,
                    updated_tool=updated_tool
                )

                tool_results.append(ToolResult(
                    tool_name=updated_tool.tool_name,
                    input_data=updated_tool.input_data,
                    output=result
                ))

                logger.debug(f"Tool invocation result: {result}")

                previous_result.append(result)
            except Exception as e:
                logger.error(f"Failed to invoke tool '{tool.tool_name}' at step {idx}: {e}")
                fallback_prompt = self.create_fallback_response(state, error_message=str(e))
                
                self._invoke_streamed_response(
                    agent_name="chat_agent",
                    session_id=state["session_id"],
                    user_input=user_input,
                    result_channel=result_channel,
                    tool_summaries_str=tool_summaries_str,
                    chat_history_str=conversation_session.get_last_n_messages(10)
                )
                return None

        self._invoke_streamed_response(
            agent_name="summary_agent",
            session_id=state["session_id"],
            user_input=user_input,
            result_channel=result_channel,
            tool_summaries_str=tool_summaries_str,
            chat_history_str=conversation_session.get_last_n_messages(10),
            final_result=format_final_summary_result(tool_results)
        )

        return None

    async def _invoke_and_store_tool(
            self,
            user_input: str,
            mcp_service: MCPService,
            updated_tool: ToolInvocation,
            conversation_session: ConversationSession,
    ):
        result: Dict[str, Any] = await mcp_service.invoke_tool(
            tool_name=updated_tool.tool_name,
            input_data=updated_tool.input_data
        )

        conversation_session.add_message({
            "role": "user",
            "content": user_input
        })

        conversation_session.add_message({
            "role": "assistant",
            "content": json.dumps(result)
        })

        return result

    def create_fallback_response(self, state: MultiAgentStepState, error_message: Optional[str] = None) -> str:
        if error_message:
            fallback_prompt = (
                f"There was a problem invoking a tool for this user input: {state['query']}.\n"
                f"Error details: {error_message}\n"
                "Please provide a helpful, conversational response for the user, suggest next steps or ask a clarifying question."
            )
        else:
            fallback_prompt = (
                f"Failed to invoke a tool for this user input: {state['query']}.\n"
                "Please provide a helpful conversational response, summary, or ask a clarifying question."
            )

        return fallback_prompt

    def _send_progress_update(self, session_id: str, result_channel: str, tool_name: str, progress_step: int, tool_len: int, message: str) -> None:
        from worker.tasks import send_progress_update
        send_progress_update.delay(
            session_id=session_id,
            result_channel=result_channel,
            tool_name=tool_name,
            progress_step=progress_step,
            tool_len=tool_len,
            message=message
        )

    def _invoke_streamed_response(self, agent_name: str, session_id: str, user_input: str, result_channel: str, tool_summaries_str: str, chat_history_str: str, final_result: str | None = None) -> None:
        from worker.tasks import invoke_streamed_response
        invoke_streamed_response.delay(
            agent_name=agent_name,
            session_id=session_id,
            user_input=user_input,
            result_channel=result_channel,
            tool_summaries_str=tool_summaries_str,
            chat_history_str=chat_history_str,
            final_result=final_result
        )

    async def run(
            self,
            session_id: str,
            result_channel: str,
            query: str,
            tool_summaries_str: str,
            mcp_service: MCPService,
            conversation_session: ConversationSession,
    ) -> None:
        initial_state = MultiAgentStepState(
            session_id=session_id,
            query=query,
            mcp_service=mcp_service,
            tool_summaries_str=tool_summaries_str,
            tool_invocations=ToolInvocations(tools=[]),
            result_channel=result_channel,
            conversation_session=conversation_session
        )

        return await self.graph.ainvoke(initial_state)
