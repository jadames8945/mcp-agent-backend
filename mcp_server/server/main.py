from dotenv import load_dotenv
from fastmcp import FastMCP

from mcp_server.server.agents.research_agent import ResearchAgent
from mcp_server.server.graph.calculator_graph import CalculatorGraph
from mcp_server.server.schemas.calculation_result import CalculationResult
from mcp_server.server.schemas.finance_result import FundDetails
from mcp_server.server.schemas.research_response import ResearchResponse
from mcp_server.server.tools.finance.tool import get_fund_details

load_dotenv()
mcp = FastMCP()


@mcp.tool(name="calculation_tool", description="Evaluates a mathematical expression and returns the result.")
def calculation_tool(expression: str) -> CalculationResult:
    """
        Evaluates a mathematical expression and returns the result.

        Args:
            expression (str): The mathematical expression provided by the user to be evaluated.

        Returns:
            CalculationResult: A data structure containing the results of the calculation, including:
                               - calculation_id: A unique identifier for the calculation.
                               - input_expression: The original mathematical expression.
                               - result_value: The computed result of the expression.
                               - success: A boolean indicating whether the calculation was successful.
                               - error_message: An optional error message if the calculation fails.
                               - timestamp: An optional timestamp of when the calculation was performed.
    """
    return CalculatorGraph().run(expression)


@mcp.tool(name="research_tool",
          description="Conducts research using Wikipedia based on a user's question and returns summarized findings.")
def research_tool(research_question: str) -> ResearchResponse:
    """
        Conducts research based on a user's question and returns summarized findings.

        Args:
            research_question (str): The question provided by the user for which research is to be conducted.

        Returns:
            ResearchResponse: A data structure containing the research results, including:
                              - question: The original research question.
                              - answer_summary: A summary of the findings related to the research question.
                              - source: A list of Source objects, each containing:
                                - title: The title of the source.
                                - url: The URL of the source.
    """
    return ResearchAgent().fetch_research_results(research_question)


@mcp.tool(name="finance_tool", 
          description="Looks up mutual fund information by its ticker symbol using Yahoo Finance.")
def finance_tool(ticker: str) -> FundDetails:
    """
    Looks up mutual fund information by its ticker symbol using Yahoo Finance.

    Args:
        ticker (str): The ticker symbol of the mutual fund to look up.

    Returns:
        FinanceResult: A data structure containing the financial information of the mutual fund, including:
                        - query_id: A unique identifier for the query.
                        - query_text: The original query text.
                        - finance_result: A FundSummary containing the fund's classification, details, and source.
                        - is_successful: A boolean indicating whether the lookup was successful.
                        - searched_at: An optional timestamp of when the lookup was performed.
                        - error_message: An optional error message if the lookup fails.
    """
    return get_fund_details(ticker)


if __name__ == '__main__':
    mcp.run(transport="sse", host="0.0.0.0", port=9000)
