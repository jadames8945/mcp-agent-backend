from typing import Optional, TypedDict

from mcp_server.server.schemas.calculation_result import CalculationResult


class CalculatorState(TypedDict):
    query: str
    calculated_results: Optional[CalculationResult]
    validated_results: Optional[CalculationResult]
