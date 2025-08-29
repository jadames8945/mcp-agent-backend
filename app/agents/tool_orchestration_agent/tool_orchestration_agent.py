import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agents.tool_orchestration_agent.tool_orchestration_prompts import AGENT_ROLE, STRICT_TOOL_RULES, \
    CONTEXT_FIRST_RULES, \
    TOOL_SELECTION_RULES, STRICT_RULES, EXAMPLES, OUTPUT_REQUIREMENTS
from app.caches.conversation_store import ConversationSession
from app.schemas.tool_invocation import ToolInvocations
from app.utils.chat_util import chat_history_to_str
from common.utils.agent_utils import Utils

logger = logging.getLogger(__name__)


class ToolOrchestrationAgent:
    def __init__(self) -> None:
        self.parser = PydanticOutputParser(pydantic_object=ToolInvocations)
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {AGENT_ROLE}

                    **Conversation Context:**
                    - Chat history: 
                    {{chat_history}}
                                     
                    **Tool reference:** Here is the list of available tools, including the parameter names and types. 
                    You MUST use the parameter names and types exactly as shown for each tool:
                    {{available_tools}}

                    {STRICT_TOOL_RULES}
                    
                    {CONTEXT_FIRST_RULES}
                    
                    {TOOL_SELECTION_RULES}
                    
                    {STRICT_RULES}
                    
                    {EXAMPLES}
                    
                    {OUTPUT_REQUIREMENTS}
                    
                    Always return a valid JSON object:
                    {{format_instructions}}
                    """
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def _build_query_prompt(
            self,
            user_input: str
    ) -> str:
        return (
            f"User input: {user_input}\n"
            "Your job is to select which tool(s) to invoke from the provided list, and for each, "
            "provide the input_data (mapping parameter names to values from the user input), and the rank (invocation order). "
            "For example, if the user input includes multiple actions like 'do x, do y and do z', decide which tool handles each, "
            "and provide separate entries for each in the JSON array. "
        )

    def invoke_multi_step_agent(
            self,
            tool_summaries_str: str,
            user_input: str,
            conversation_session: ConversationSession,
    ) -> ToolInvocations:
        """
        Invokes the agent to determine which tools to call (with input_data and rank), based on user input.
        """
        try:
            logger.info("Invoking multi-step agent with user input: %s", user_input)

            prompt_str: str = self._build_query_prompt(user_input=user_input)

            chat_history = conversation_session.get_last_n_messages(n=10)

            utils = Utils[ToolInvocations]

            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.0,
                max_tokens=2000,
                model_kwargs={"response_format": {"type": "json_object"}}
            )

            response: ToolInvocations | None = utils.run_agent_query(
                llm=llm,
                tools=[],
                parser=self.parser,
                prompt=self.prompt,
                query=prompt_str,
                chat_history=chat_history,
                available_tools=tool_summaries_str,
                allowed_tool_names=None,
                previous_result=""
            )
        except Exception as exc:
            logger.exception("Error invoking agent: %s", exc)
            raise RuntimeError("Failed to invoke Tool Orchestration agent") from exc

        if not response:
            logger.warning("No tools matched the user input.")
            raise ValueError("Could not match any tools to user input.")

        logger.info(f"Orchestrator Agent Response: {response}.")

        return response
