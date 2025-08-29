import logging

from langchain_core.prompts import ChatPromptTemplate

from app.agents.summary_agent.summary_prompts import (
    AGENT_ROLE,
    WORKFLOW_START_INSTRUCTIONS,
    WORKFLOW_UPDATE_INSTRUCTIONS,
    WORKFLOW_COMPLETE_INSTRUCTIONS,
    CRITICAL_SCHEMA_REQUIREMENTS
)

logger = logging.getLogger(__name__)


class SummaryAgent:
    def __init__(self) -> None:
        self._prompt = self.build_prompt()

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""
                    {AGENT_ROLE}

                    {WORKFLOW_START_INSTRUCTIONS}

                    {WORKFLOW_UPDATE_INSTRUCTIONS}

                    {WORKFLOW_COMPLETE_INSTRUCTIONS}

                    {CRITICAL_SCHEMA_REQUIREMENTS}   
                         
                    **Conversation Context:**
                    - Chat history: 
                    {{chat_history}}
                    
                    User input:
                    {{final_result}}
                    
                    Respond in clear, friendly, natural language using markdown formatting for better readability.           
                    """
                ),
                ("human", "{final_result}"),
                ("placeholder", "{agent_scratchpad}")
            ]
        )

    def prompt(self) -> ChatPromptTemplate:
        return self._prompt
