from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common.utils.agent_utils import Utils
from common.utils.validator import validate_query_not_empty
from mcp_server.server.schemas.search_result import SearchResponse
from mcp_server.server.tools.search_tool import search_tool


class SearchAgent:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=SearchResponse)

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system,"
                    """
                    You are a smart and resourceful assistant.
                    Your job is to answer the user questions by searching for the relevant and accurate information.
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

    def answer_query_with_search(self, query: str) -> SearchResponse:
        validate_query_not_empty(query)

        utils = Utils[SearchResponse]

        parsed_response: Optional[SearchResponse] = utils.run_agent_query(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            tools=[search_tool()],
            parser=self.parser,
            prompt=self.build_prompt(),
            query=query,
            chat_history=""
        )

        return utils.is_null_or_empty(parsed_object=parsed_response)
