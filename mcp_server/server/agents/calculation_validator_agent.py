from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from common.utils.agent_utils import Utils
from common.utils.validator import validate_query_not_empty
from mcp_server.server.schemas.calculation_result import CalculationResult
from mcp_server.server.tools.calculation_tool import calculator_tool


class CalculationValidatorAgent:
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=CalculationResult)

    def build_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system,"
                    """
                    You are a calculation validator.
                    Your job is to carefully review and verify that your calculation is accurate.
                    Double check the math step-by-step to ensure there no mistakes.
                    If the calculation is incorrect, provide the correct calculation along with an explanation.
                    Use the available calculator tool to evaluate expressions.
                    Wrap the object in this format and provide no other tools.\n{format_instructions}
                    """
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{query}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        ).partial(format_instructions=self.parser.get_format_instructions())

    def validate_calculation(self, calculated_result: CalculationResult) -> CalculationResult:
        validate_query_not_empty(calculated_result)

        utils = Utils[CalculationResult]

        parsed_response: Optional[CalculationResult] = utils.run_agent_query(
            llm=ChatOpenAI(model="gpt-4o-mini"),
            tools=[calculator_tool()],
            parser=self.parser,
            prompt=self.build_prompt(),
            query=f"Expression: {calculated_result.input_expression}, Result: {calculated_result.result_value}",
            chat_history={}
        )

        return utils.is_null_or_empty(parsed_object=parsed_response)
