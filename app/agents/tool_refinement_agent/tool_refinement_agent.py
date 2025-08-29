import json
import logging
from typing import List, Dict, Any

from app.agents.tool_refinement_agent.tool_refinement_prompts import (
    AGENT_ROLE,
    ACCURACY_REQUIREMENT,
    VALIDATION_TASKS,
    EXAMPLES,
    CRITICAL_RULES,
    OUTPUT_REQUIREMENTS
)
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.caches.conversation_store import ConversationSession
from app.schemas.tool_invocation import ToolInvocation
from app.utils.chat_util import chat_history_to_str
from common.utils.agent_utils import Utils

logger = logging.getLogger(__name__)


class ToolRefinementAgent:
    def __init__(self) -> None:
        self.parser = PydanticOutputParser(pydantic_object=ToolInvocation)
        self.prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {AGENT_ROLE}

                    Previous tool results:
                    {{previous_result}}
                    
                    Chat history:
                    {{chat_history}}
                    
                    Available tools:
                    {{available_tools}}
                    
                    {ACCURACY_REQUIREMENT}
                    
                    {VALIDATION_TASKS}
                    
                    {EXAMPLES}
                    
                    {CRITICAL_RULES}
                    
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
            user_input: str,
            tool_invocation: ToolInvocation
    ) -> str:
        return (
            f"Original user input: {user_input}\\n\\n"
            f"Tool invocation to validate and refine:\\n{tool_invocation}\\n\\n"
            "CRITICAL: You must achieve 95%+ accuracy. Missing details will cause workflow failures.\\n\\n"
            "Please perform these tasks with HIGH PRECISION:\\n"
            "1. Validate the tool_name against the available tools list\\n"
            "2. CHECK THE TOOL'S PARAMETER LIST - ONLY use parameters that are explicitly listed\\n"
            "3. Extract ALL specific details from user input (IDs, emails, names, numbers, etc.)\\n"
            "4. Extract ALL specific details from previous results (fund data, research findings, etc.)\\n"
            "5. Enhance parameters with missing details while preserving exact structure\\n"
            "6. NEVER add parameters that aren't in the tool's schema\\n"
            "7. For 'ticker' parameters, use exact ticker symbols only\\n"
            "8. For 'instruction' parameters, include comprehensive details\\n\\n"
            "PARAMETER COMPLIANCE CHECK:\\n"
            "- Look at the tool's parameter list in the available_tools\\n"
            "- ONLY use parameters that are explicitly listed for that specific tool\\n"
            "- NEVER add parameters that aren't in the tool's parameter list\\n"
            "- Preserve the exact parameter names and types as defined\\n\\n"
            "Return the refined tool invocation with EXACT parameter compliance."
        )

    def refine_tool_invocation(
            self,
            user_input: str,
            tool_summaries_str: str,
            conversation_session: ConversationSession,
            previous_result: List[Dict[str, Any]],
            tool_invocation: ToolInvocation,
    ) -> ToolInvocation:
        logger.info("Invoking Tool Refinement agent")

        chat_history = conversation_session.get_last_n_messages(10)

        query_prompt: str = self._build_query_prompt(
            user_input=user_input,
            tool_invocation=tool_invocation,
        )

        utils = Utils[ToolInvocation]

        response: ToolInvocation | None = utils.run_agent_query(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            tools=[],
            query=query_prompt,
            parser=self.parser,
            prompt=self.prompt,
            chat_history=chat_history,
            available_tools=tool_summaries_str,
            allowed_tool_names=None,
            previous_result=json.dumps(previous_result, indent=2)
        )

        if not response:
            logger.warning("ToolRefinementAgent: No response for tool invocation update.")
            return tool_invocation

        logger.info(f"ToolRefinementAgent: Updated tool invocation: {response}")

        return response
