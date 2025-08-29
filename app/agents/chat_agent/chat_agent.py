import logging

from langchain_core.prompts import ChatPromptTemplate

from app.agents.chat_agent.chat_prompts import AGENT_ROLE, AGENT_GOALS

logger = logging.getLogger(__name__)


class ChatAgent:
    def __init__(self) -> None:
        self._prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {AGENT_ROLE}

                    {AGENT_GOALS}
                    
                    Context available to you:
                    {{chat_history}}
                    
                    The following is a list of all tools you are able to use, with their server, name, description, and parameters:
                    {{available_tools}}
                    
                    User input:
                    {{user_input}}
                    
                    Respond in clear, friendly, natural language. Do not use any special formatting or JSON structure.
                    """
                ),
                ("human", "{user_input}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        )

    def prompt(self) -> ChatPromptTemplate:
        return self._prompt
