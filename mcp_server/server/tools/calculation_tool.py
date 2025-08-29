import requests
from langchain_core.tools import Tool


def calculator_tool() -> Tool:
    """
    A calculator tool that evaluates a given expression using MathJS API.
    """
    return Tool(
        name="calculator",
        func=_calculator_func,
        description="Evaluate a given Math expression. Input should be a valid expression like '2 + 3 * 4'"
    )


def _calculator_func(expression: str) -> str:
    response = requests.get("https://api.mathjs.org/v4/", params={"expr": expression})

    if response.status_code != 200:
        return f"Error calculating expression {response.text}"

    return response.text.strip()
