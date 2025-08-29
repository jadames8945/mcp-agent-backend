from typing import Optional

from pydantic import BaseModel


class CalculationResult(BaseModel):
    calculation_id: str
    input_expression: str
    result_value: float
    success: bool
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
