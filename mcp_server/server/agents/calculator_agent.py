from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common.utils.agent_utils import Utils
from mcp_server.server.schemas.calculation_result import CalculationResult
from mcp_server.server.tools.calculation_tool import calculator_tool


class CalculatorAgent:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=CalculationResult)

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system,"
                    """
                    You are a math expert.
                    Your job is to solve math problems and return the correct answer. .
                    use the available calculator tool to evaluate expressions.
                    Wrap the object in this format and provide no other tools.\n{format_instructions}
                    """
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def calculate_expression(self, query: str) -> CalculationResult:
        if not query:
            raise Exception("Query is empty. Please enter a value and try again!")

        utils = Utils[CalculationResult]

        parsed_response: Optional[CalculationResult] = utils.run_agent_query(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            tools=[calculator_tool()],
            parser=self.parser,
            prompt=self.build_prompt(),
            query=query,
            chat_history={}
        )

        return utils.is_null_or_empty(parsed_object=parsed_response)
