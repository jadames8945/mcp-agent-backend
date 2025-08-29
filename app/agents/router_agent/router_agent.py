import logging

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.agents.router_agent.router_prompts import AGENT_ROLE, ROUTING_RULES, EXAMPLES
from app.caches.conversation_store import ConversationSession
from app.schemas.router_decision import RouterDecision
from common.utils.agent_utils import Utils
from app.utils.chat_util import chat_history_to_str

logger = logging.getLogger(__name__)


class RouterAgent:
    def __init__(self) -> None:
        self.parser = PydanticOutputParser(pydantic_object=RouterDecision)
        self.router_prompt = self.build_router_prompt()

    def build_router_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {AGENT_ROLE}
                    
                    Here is the list of available tools:
                    {{available_tools}}
                    
                    Context available to you:
                    {{chat_history}}
                    
                    {ROUTING_RULES}
                    
                    {EXAMPLES}
                    
                    Always return a valid JSON object:
                    {{format_instructions}}
                    """
                ),
                ("human", "{query}"),
                ("placeholder", "{chat_history}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def handle_router_decision(
            self,
            user_input: str,
            tool_summaries_str: str,
            conversation_session: ConversationSession,
    ) -> RouterDecision:
        logger.debug(f"Inside router Agent UserInput: {user_input}")
        logger.debug(f"tool_summaries_str: {tool_summaries_str}")
        chat_history = conversation_session.get_last_n_messages(n=10)

        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.8,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        utils = Utils[RouterDecision]


        result: RouterDecision = utils.run_agent_query(
            llm=llm,
            tools=[],
            query=user_input,
            parser=self.parser,
            prompt=self.router_prompt,
            chat_history=chat_history,
            available_tools=tool_summaries_str,
            allowed_tool_names=None,
            previous_result = None
        )
        if not result:
            raise Exception("Could not route")

        logger.info(f"Router decision result: {result}")

        return result
