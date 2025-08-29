from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common.utils.agent_utils import Utils
from common.utils.validator import validate_query_not_empty
from mcp_server.server.schemas.research_response import ResearchResponse
from mcp_server.server.tools.wiki_tool import wiki_tool


class ResearchAgent:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=ResearchResponse)

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system,"
                    """
                    You are a helpful and knowledgeable research assistant.
                    Your job is to thoroughly research the following question using the available tools and provide:
                    - A clear concise summary of the answer.
                    - A list of reliable sources (with title and URL) to back up your response.
                    Use the search tools provided to look up and gather the most relevant and recent information.
                    Do fabricate answers. If information cannot be found, state that clearly.
                    Wrap the object in this format and provide no other tools.\n{format_instructions}
                    """
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def fetch_research_results(self, question: str, chat_history: str = "") -> ResearchResponse:
        validate_query_not_empty(question)

        utils = Utils[ResearchResponse]

        parsed_response: Optional[ResearchResponse] = utils.run_agent_query(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            tools=[wiki_tool()],
            parser=self.parser,
            prompt=self.build_prompt(),
            query=question,
            chat_history=chat_history
        )

        return utils.is_null_or_empty(parsed_object=parsed_response)
